#!/bin/bash
set -euo pipefail

# =============================================================================
# PRODUCTION DEPLOYMENT SCRIPT FOR SIMPLEAPP TRADING MIDDLEWARE
# =============================================================================
# This script deploys the application to production with all necessary
# security, monitoring, and optimization configurations
# =============================================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="SimpleApp"
APP_VERSION="1.0.0"
DEPLOY_DIR="/opt/simpleapp"
BACKUP_DIR="/opt/backups/simpleapp"
LOG_DIR="/var/log/simpleapp"
SERVICE_USER="simpleapp"
SERVICE_GROUP="simpleapp"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if required commands exist
    local required_commands=("docker" "docker-compose" "systemctl" "nginx" "openssl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            print_warning "Command $cmd not found. Some features may not work."
        fi
    done
    
    # Check if required directories exist
    local required_dirs=("/opt" "/var/log" "/etc/systemd/system")
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            print_error "Required directory $dir does not exist"
            exit 1
        fi
    done
    
    print_success "Prerequisites check completed"
}

# Function to create service user
create_service_user() {
    print_status "Creating service user and group..."
    
    if ! id "$SERVICE_USER" &>/dev/null; then
        useradd -r -s /bin/false -d "$DEPLOY_DIR" "$SERVICE_USER"
        print_success "Created service user: $SERVICE_USER"
    else
        print_status "Service user $SERVICE_USER already exists"
    fi
    
    if ! getent group "$SERVICE_GROUP" &>/dev/null; then
        groupadd "$SERVICE_GROUP"
        print_success "Created service group: $SERVICE_GROUP"
    else
        print_status "Service group $SERVICE_GROUP already exists"
    fi
    
    # Add user to group
    usermod -a -G "$SERVICE_GROUP" "$SERVICE_USER"
}

# Function to create directories
create_directories() {
    print_status "Creating application directories..."
    
    local dirs=("$DEPLOY_DIR" "$BACKUP_DIR" "$LOG_DIR" "/etc/simpleapp" "/var/cache/simpleapp")
    
    for dir in "${dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        else
            print_status "Directory already exists: $dir"
        fi
    done
    
    # Set proper permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$DEPLOY_DIR" "$LOG_DIR" "/var/cache/simpleapp"
    chmod 755 "$DEPLOY_DIR" "$LOG_DIR" "/var/cache/simpleapp"
    chmod 700 "/etc/simpleapp"
}

# Function to backup existing installation
backup_existing() {
    if [[ -d "$DEPLOY_DIR" && "$(ls -A "$DEPLOY_DIR")" ]]; then
        print_status "Backing up existing installation..."
        
        local backup_name="backup-$(date +%Y%m%d-%H%M%S)"
        local backup_path="$BACKUP_DIR/$backup_name"
        
        mkdir -p "$backup_path"
        cp -r "$DEPLOY_DIR"/* "$backup_path/"
        
        print_success "Backup created at: $backup_path"
    fi
}

# Function to deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Copy application files
    cp -r . "$DEPLOY_DIR/"
    
    # Remove unnecessary files
    cd "$DEPLOY_DIR"
    rm -rf .git .venv __pycache__ *.pyc .DS_Store
    
    # Set proper permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$DEPLOY_DIR"
    chmod +x "$DEPLOY_DIR/start_production.sh"
    
    print_success "Application deployed to: $DEPLOY_DIR"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Copy environment template
    if [[ -f "production_env_template.txt" ]]; then
        cp production_env_template.txt /etc/simpleapp/.env
        chown "$SERVICE_USER:$SERVICE_GROUP" /etc/simpleapp/.env
        chmod 600 /etc/simpleapp/.env
        
        print_warning "Please edit /etc/simpleapp/.env with your production values"
        print_warning "Critical: Change SECRET_KEY and other sensitive values"
    else
        print_error "Environment template not found"
        exit 1
    fi
}

# Function to setup virtual environment
setup_virtual_environment() {
    print_status "Setting up Python virtual environment..."
    
    cd "$DEPLOY_DIR"
    
    # Create virtual environment
    python3 -m venv .venv
    
    # Activate and install dependencies
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Set proper permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" .venv
    
    print_success "Virtual environment setup completed"
}

# Function to create systemd service
create_systemd_service() {
    print_status "Creating systemd service..."
    
    local service_file="/etc/systemd/system/simpleapp.service"
    
    cat > "$service_file" << EOF
[Unit]
Description=SimpleApp Trading Middleware
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$DEPLOY_DIR
Environment=PATH=$DEPLOY_DIR/.venv/bin
EnvironmentFile=/etc/simpleapp/.env
ExecStart=$DEPLOY_DIR/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=simpleapp

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$LOG_DIR /var/cache/simpleapp
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictSUIDSGID=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable simpleapp.service
    
    print_success "Systemd service created and enabled"
}

# Function to setup Nginx configuration
setup_nginx() {
    if command -v nginx &> /dev/null; then
        print_status "Setting up Nginx configuration..."
        
        local nginx_conf="/etc/nginx/sites-available/simpleapp"
        local nginx_enabled="/etc/nginx/sites-enabled/simpleapp"
        
        cat > "$nginx_conf" << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/simpleapp.crt;
    ssl_certificate_key /etc/ssl/private/simpleapp.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files
    location /static/ {
        alias $DEPLOY_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
        
        # Enable site
        ln -sf "$nginx_conf" "$nginx_enabled"
        
        # Test configuration
        if nginx -t; then
            systemctl reload nginx
            print_success "Nginx configuration completed"
        else
            print_error "Nginx configuration test failed"
            exit 1
        fi
    else
        print_warning "Nginx not found, skipping Nginx configuration"
    fi
}

# Function to setup SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    local ssl_dir="/etc/ssl"
    local cert_file="$ssl_dir/certs/simpleapp.crt"
    local key_file="$ssl_dir/private/simpleapp.key"
    
    # Create SSL directory if it doesn't exist
    mkdir -p "$ssl_dir/certs" "$ssl_dir/private"
    
    # Generate self-signed certificate (replace with real certificate in production)
    if [[ ! -f "$cert_file" ]] || [[ ! -f "$key_file" ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$key_file" \
            -out "$cert_file" \
            -subj "/C=IN/ST=State/L=City/O=Organization/CN=your-domain.com"
        
        chmod 644 "$cert_file"
        chmod 600 "$key_file"
        
        print_warning "Self-signed certificate generated. Replace with real certificate in production."
    fi
    
    print_success "SSL certificates setup completed"
}

# Function to setup firewall
setup_firewall() {
    print_status "Setting up firewall rules..."
    
    if command -v ufw &> /dev/null; then
        # UFW firewall
        ufw allow 22/tcp    # SSH
        ufw allow 80/tcp    # HTTP
        ufw allow 443/tcp   # HTTPS
        ufw allow 8000/tcp  # Application (if not using Nginx)
        
        ufw --force enable
        print_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        # firewalld
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-port=8000/tcp
        
        firewall-cmd --reload
        print_success "firewalld configured"
    else
        print_warning "No supported firewall found, skipping firewall configuration"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring and logging..."
    
    # Create logrotate configuration
    local logrotate_conf="/etc/logrotate.d/simpleapp"
    
    cat > "$logrotate_conf" << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $SERVICE_USER $SERVICE_GROUP
    postrotate
        systemctl reload simpleapp.service > /dev/null 2>&1 || true
    endscript
}
EOF
    
    # Setup log directory permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$LOG_DIR"
    chmod 755 "$LOG_DIR"
    
    print_success "Monitoring and logging setup completed"
}

# Function to setup backup
setup_backup() {
    print_status "Setting up backup configuration..."
    
    local backup_script="$DEPLOY_DIR/backup.sh"
    
    cat > "$backup_script" << 'EOF'
#!/bin/bash
# Backup script for SimpleApp

BACKUP_DIR="/opt/backups/simpleapp"
APP_DIR="/opt/simpleapp"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="simpleapp-backup-$DATE.tar.gz"

# Create backup
tar -czf "$BACKUP_DIR/$BACKUP_NAME" -C "$APP_DIR" .

# Remove old backups (keep last 30 days)
find "$BACKUP_DIR" -name "simpleapp-backup-*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_NAME"
EOF
    
    chmod +x "$backup_script"
    chown "$SERVICE_USER:$SERVICE_GROUP" "$backup_script"
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $backup_script") | crontab -
    
    print_success "Backup configuration completed"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start application service
    systemctl start simpleapp.service
    
    # Check service status
    if systemctl is-active --quiet simpleapp.service; then
        print_success "SimpleApp service started successfully"
    else
        print_error "Failed to start SimpleApp service"
        systemctl status simpleapp.service
        exit 1
    fi
    
    # Reload Nginx if configured
    if command -v nginx &> /dev/null; then
        systemctl reload nginx
        print_success "Nginx reloaded"
    fi
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Wait for service to be ready
    sleep 10
    
    # Check if service is responding
    if curl -f http://localhost:8000/api/healthz > /dev/null 2>&1; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        exit 1
    fi
    
    # Check if Nginx is working
    if command -v nginx &> /dev/null; then
        if curl -f http://localhost/health > /dev/null 2>&1; then
            print_success "Nginx health check passed"
        else
            print_warning "Nginx health check failed"
        fi
    fi
}

# Function to display deployment summary
display_summary() {
    print_success "Deployment completed successfully!"
    echo
    echo "=== DEPLOYMENT SUMMARY ==="
    echo "Application: $APP_NAME v$APP_VERSION"
    echo "Installation Directory: $DEPLOY_DIR"
    echo "Service User: $SERVICE_USER"
    echo "Log Directory: $LOG_DIR"
    echo "Backup Directory: $BACKUP_DIR"
    echo
    echo "=== NEXT STEPS ==="
    echo "1. Edit /etc/simpleapp/.env with your production values"
    echo "2. Replace SSL certificate with real certificate"
    echo "3. Configure your domain in Nginx configuration"
    echo "4. Test all functionality"
    echo "5. Monitor logs: journalctl -u simpleapp.service -f"
    echo "6. Setup monitoring and alerting"
    echo
    echo "=== USEFUL COMMANDS ==="
    echo "Start service: systemctl start simpleapp.service"
    echo "Stop service: systemctl stop simpleapp.service"
    echo "Restart service: systemctl restart simpleapp.service"
    echo "View logs: journalctl -u simpleapp.service -f"
    echo "View status: systemctl status simpleapp.service"
    echo
    echo "=== SECURITY REMINDERS ==="
    echo "✅ Change default passwords and keys"
    echo "✅ Configure firewall rules"
    echo "✅ Setup SSL certificates"
    echo "✅ Enable monitoring and alerting"
    echo "✅ Regular backups and updates"
}

# Main deployment function
main() {
    echo "=========================================="
    echo "  SIMPLEAPP PRODUCTION DEPLOYMENT SCRIPT"
    echo "=========================================="
    echo
    
    check_root
    check_prerequisites
    create_service_user
    create_directories
    backup_existing
    deploy_application
    setup_environment
    setup_virtual_environment
    create_systemd_service
    setup_ssl
    setup_nginx
    setup_firewall
    setup_monitoring
    setup_backup
    start_services
    run_health_checks
    display_summary
}

# Run main function
main "$@"
