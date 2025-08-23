# WhatsApp Bulk Messaging System

## Overview
This project is a Flask-based web application designed for sending bulk WhatsApp messages. It enables users to upload lead lists, create personalized message templates with variables and interactive buttons, and monitor message delivery in real-time. The system aims to provide a robust solution for businesses to engage with their audience through personalized WhatsApp communication, leveraging high-speed message delivery capabilities.

## User Preferences
Preferred communication style: Simple, everyday language.

## System Architecture

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Session Management**: Flask sessions
- **Logging**: Python logging
- **Middleware**: ProxyFix for reverse proxy deployments

### Frontend
- **Template Engine**: Jinja2
- **UI Framework**: Bootstrap (dark theme)
- **Icons**: Font Awesome 6.0
- **JavaScript**: Vanilla JS, class-based
- **Real-time Updates**: Polling-based status checking

### Core Features
- **Lead Management**: Bulk import, validation (CPF, phone numbers), and duplicate filtering.
- **Message Templating**: Personalized messages using variables ({nome}, {cpf}, {numero}), interactive buttons with URL personalization.
- **Campaign Management**: Creation, real-time progress monitoring, and status tracking.
- **Ultra-Speed Messaging**: Optimized for high-throughput, supporting parallel processing with automatic load balancing across multiple WhatsApp Phone Numbers. **Each phone number supports up to 10,000 messages per batch** (increased from 1,000).
- **Dynamic API Integration**: Automatic discovery and configuration of WhatsApp Business Manager IDs, Phone Number IDs, and available templates based on the provided access token.
- **Robust Error Handling**: Intelligent fallback mechanisms (where applicable), automatic retries, and comprehensive logging.
- **Deployment**: Optimized for Heroku with support for various dyno configurations.
- **Anti-Duplication**: Tracks successfully sent numbers in a database to prevent re-sending to the same contacts.

### System Design
- **Scalability**: Designed to handle large volumes of messages through multi-threading, connection pooling, and distributed sending across multiple WhatsApp Phone Numbers.
- **Modularity**: Separation of concerns with distinct models, services, and utilities.
- **User Experience**: Intuitive interface with real-time progress indicators, message previews, and streamlined workflow.
- **Security**: Environment variable-based configuration for sensitive data like API tokens and database credentials.

## External Dependencies

### Services
- **WhatsApp Business API**: Primary service for sending WhatsApp messages.

### Environment Variables
- `WHATSAPP_ACCESS_TOKEN`: Required for WhatsApp Business API authentication.
- `DATABASE_URL`: PostgreSQL database connection string.
- `SESSION_SECRET`: Flask session secret key (optional, has development default).

### Libraries
- `Flask`: Web framework.
- `Flask-SQLAlchemy`: ORM for database interaction.
- `Requests`: HTTP library for API communication.
- `Werkzeug`: WSGI utilities.
- `psycopg2-binary`: PostgreSQL adapter.

### Frontend Libraries (via CDN)
- `Bootstrap`
- `Font Awesome`
```