# WhatsApp Chat Business API System

## Overview
This project is a Flask-based web application designed for WhatsApp Business API chat functionality. It provides webhook integration for receiving client messages, conversational automation, and a clean interface for managing WhatsApp Business connections. The system focuses on real-time chat interactions and automated conversation flows.

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
- **Webhook Integration**: Real-time webhook processing for receiving WhatsApp messages from clients.
- **Dynamic API Integration**: Automatic discovery and configuration of WhatsApp Business Manager IDs, Phone Number IDs, and available templates based on the provided access token.
- **Robust Error Handling**: Intelligent fallback mechanisms (where applicable), automatic retries, and comprehensive logging.
- **Deployment**: Optimized for Replit with support for both development and production environments.

### **Conversational Automation System**
- **Dual Conversation Flows**: Automatic detection of Recoverify API status (APPROVED vs PENDING) with conditional message flows
- **CPF Validation & API Integration**: Real-time CPF validation using external Recoverify API with personalized responses
- **OpenAI Integration**: GPT-5 powered intelligent responses for customer questions with specialized Shopee delivery context
- **Audio Message Processing**: Complete Whisper-powered audio transcription and GPT-5 text responses for voice messages
- **Interactive Button System**: WhatsApp native buttons for seamless user experience (Yes/No, confirmation flows)
- **Persistent State Management**: Database-backed conversation states supporting complex multi-step interactions
- **Smart Conversion System**: 10 total attempts (5 questions + 5 professional conversion messages) with formal tone
- **Dynamic Payment Links**: Personalized payment URLs using original CPF format (https://shopee.acesso.inc/{cpf})
- **Typing Indicator Simulation**: Intelligent delay system (1-4 seconds based on message length) before all message types for natural conversation flow

### System Design
- **Scalability**: Designed to handle real-time chat interactions with efficient webhook processing and conversation state management.
- **Modularity**: Separation of concerns with distinct models, services, and utilities.
- **User Experience**: Intuitive interface with webhook configuration, WhatsApp Business connection, and chat functionality.
- **Security**: Environment variable-based configuration for sensitive data like API tokens and database credentials.

## External Dependencies

### Services
- **WhatsApp Business API**: Primary service for sending WhatsApp messages.
- **OpenAI API**: GPT-5 for intelligent conversation responses and Whisper for audio transcription.
- **Recoverify API**: External CPF validation and customer data retrieval.

### Environment Variables
- `WHATSAPP_ACCESS_TOKEN`: Required for WhatsApp Business API authentication.
- `OPENAI_API_KEY`: Required for OpenAI GPT-5 and Whisper services.
- `DATABASE_URL`: PostgreSQL database connection string.
- `SESSION_SECRET`: Flask session secret key (optional, has development default).

### Libraries
- `Flask`: Web framework.
- `Flask-SQLAlchemy`: ORM for database interaction.
- `Requests`: HTTP library for API communication.
- `Werkzeug`: WSGI utilities.
- `psycopg2-binary`: PostgreSQL adapter.
- `OpenAI`: GPT-5 and Whisper integration for conversational AI.

### Frontend Libraries (via CDN)
- `Bootstrap`
- `Font Awesome`
```