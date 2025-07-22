#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# App name
APP_NAME="Fouskoto Quiz"

# Function to print formatted messages
print_message() {
  echo -e "${GREEN}[${APP_NAME}]${NC} $1"
}

print_warning() {
  echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

print_section() {
  echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
  fi
}

# Function to backup the database
backup_database() {
  print_section "Database Backup"
  
  BACKUP_DIR="./backups"
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  BACKUP_FILE="${BACKUP_DIR}/quiz_app_db_${TIMESTAMP}.sqlite"
  
  # Create backup directory if it doesn't exist
  mkdir -p "${BACKUP_DIR}"
  
  if [ -f "./instance/quiz_app.db" ]; then
    cp "./instance/quiz_app.db" "${BACKUP_FILE}"
    print_message "Database backed up to ${BACKUP_FILE}"
  else
    print_warning "No database file found at ./instance/quiz_app.db"
    return 1
  fi
}

# Function to restore the database
restore_database() {
  print_section "Database Restore"
  
  BACKUP_DIR="./backups"
  
  if [ ! -d "${BACKUP_DIR}" ]; then
    print_error "Backup directory ${BACKUP_DIR} does not exist."
    return 1
  fi
  
  # List all available backups
  echo "Available backups:"
  ls -1 "${BACKUP_DIR}" | grep -i "quiz_app_db" | cat -n
  
  # Ask user to select a backup
  echo ""
  read -p "Enter the number of the backup to restore (or 0 to cancel): " BACKUP_NUM
  
  if [ "${BACKUP_NUM}" -eq 0 ]; then
    print_warning "Restore cancelled."
    return 0
  fi
  
  BACKUP_FILE=$(ls -1 "${BACKUP_DIR}" | grep -i "quiz_app_db" | sed -n "${BACKUP_NUM}p")
  
  if [ -z "${BACKUP_FILE}" ]; then
    print_error "Invalid backup number."
    return 1
  fi
  
  BACKUP_PATH="${BACKUP_DIR}/${BACKUP_FILE}"
  
  if [ ! -f "${BACKUP_PATH}" ]; then
    print_error "Backup file ${BACKUP_PATH} does not exist."
    return 1
  fi
  
  # Stop any running containers
  if docker-compose ps | grep -q "Up" || docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    print_message "Stopping containers before restoring database..."
    docker-compose down 2>/dev/null
    docker-compose -f docker-compose.dev.yml down 2>/dev/null
  fi
  
  # Backup current database if it exists
  if [ -f "./instance/quiz_app.db" ]; then
    CURRENT_BACKUP="${BACKUP_DIR}/quiz_app_db_before_restore_${TIMESTAMP}.sqlite"
    cp "./instance/quiz_app.db" "${CURRENT_BACKUP}"
    print_message "Current database backed up to ${CURRENT_BACKUP}"
  fi
  
  # Restore the selected backup
  cp "${BACKUP_PATH}" "./instance/quiz_app.db"
  print_message "Database restored from ${BACKUP_PATH}"
}

# Function to build and deploy for production
deploy_production() {
  print_section "Production Deployment"
  
  # Backup database before deployment
  print_message "Backing up database before deployment..."
  backup_database
  
  print_message "Building Docker image..."
  docker-compose build
  
  if [ $? -eq 0 ]; then
    print_message "Docker image built successfully."
    
    print_message "Starting containers..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
      print_message "Production deployment successful!"
      print_message "The application is now running at http://localhost:6789"
    else
      print_error "Failed to start containers."
      exit 1
    fi
  else
    print_error "Failed to build Docker image."
    exit 1
  fi
}

# Function to build and deploy for development
deploy_development() {
  print_section "Development Deployment"
  
  print_message "Building Docker image for development..."
  docker-compose -f docker-compose.dev.yml build
  
  if [ $? -eq 0 ]; then
    print_message "Development Docker image built successfully."
    
    print_message "Starting development containers..."
    print_message "Press Ctrl+C to stop the containers when done."
    docker-compose -f docker-compose.dev.yml up
    
    if [ $? -ne 0 ]; then
      print_error "Failed to start development containers."
      exit 1
    fi
  else
    print_error "Failed to build development Docker image."
    exit 1
  fi
}

# Function to stop containers
stop_containers() {
  print_section "Stopping Containers"
  
  if [ "$1" == "dev" ]; then
    print_message "Stopping development containers..."
    docker-compose -f docker-compose.dev.yml down
  else
    print_message "Stopping production containers..."
    docker-compose down
  fi
  
  if [ $? -eq 0 ]; then
    print_message "Containers stopped successfully."
  else
    print_error "Failed to stop containers."
    exit 1
  fi
}

# Function to clean up
clean_environment() {
  print_section "Cleaning Environment"
  
  print_message "Removing all project containers and images..."
  docker-compose down --rmi all 2>/dev/null
  docker-compose -f docker-compose.dev.yml down --rmi all 2>/dev/null
  
  print_message "Removing dangling images..."
  docker image prune -f
  
  print_message "Cleanup complete."
}

# Function to show container status
show_status() {
  print_section "Container Status"
  
  echo "Production containers:"
  docker-compose ps
  
  echo -e "\nDevelopment containers:"
  docker-compose -f docker-compose.dev.yml ps
}

# Function to display usage information
show_usage() {
  echo -e "${GREEN}${APP_NAME} Deployment Script${NC}"
  echo -e "This script helps with building, deploying, and managing the ${APP_NAME} application.\n"
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  prod          Build and deploy for production (detached mode)"
  echo "  dev           Build and deploy for development (with logs)"
  echo "  stop          Stop production containers"
  echo "  stop-dev      Stop development containers"
  echo "  status        Show status of all containers"
  echo "  backup        Backup the database"
  echo "  restore       Restore the database from a backup"
  echo "  clean         Remove all containers and images related to the project"
  echo "  help          Show this help message"
  echo ""
}

# Main script logic
case "$1" in
  prod)
    check_docker
    deploy_production
    ;;
  dev)
    check_docker
    deploy_development
    ;;
  stop)
    check_docker
    stop_containers "prod"
    ;;
  stop-dev)
    check_docker
    stop_containers "dev"
    ;;
  status)
    check_docker
    show_status
    ;;
  backup)
    backup_database
    ;;
  restore)
    restore_database
    ;;
  clean)
    check_docker
    clean_environment
    ;;
  help|"")
    show_usage
    ;;
  *)
    print_error "Unknown command: $1"
    show_usage
    exit 1
    ;;
esac

exit 0
