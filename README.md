# **Kenya Rental Hub**

Kenya Rental Hub is a property rental platform built with **Django** and **Django REST Framework** (DRF). This platform allows tenants to browse available properties, apply for them, leave reviews, and make payments, while landlords can list their properties, manage applications, and approve/reject them.
<img src="./static/images/logo.png" alt="Logo" width="200"/>
## **Table of Contents**
- [Project Setup](#project-setup)
- [Features](#features)
- [Frontend Endpoints](#frontend-endpoints)
- [Django Admin](#django-admin)
- [API Endpoints](#api-endpoints)

## **Project Setup**

This project was built with the following technologies:
- **Backend**: Django, Django REST Framework (DRF)
- **Database**: MySQL (configured in `settings.py`)
- **Frontend**: HTML, CSS (Template rendering with Django's built-in template engine)
- **Authentication**: Django custom user model with roles (Tenant and Landlord)

## **Installation**

1. **Clone the Repository**:
   Clone the repository to your local machine: https://github.com/ksila01/kenyarentalhub_api


The server will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

### **Frontend Testing URL**:
- **Homepage / Property List**: [http://127.0.0.1:8000/](http://127.0.0.1:8000)
- **Property Detail**: [http://127.0.0.1:8000/properties/<property_id>/](http://127.0.0.1:8000/properties/2/)
- **Register**: [http://127.0.0.1:8000/register/](http://127.0.0.1:8000/register/)
- **Login**: [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **Create Property (Landlord)**: [http://127.0.0.1:8000/properties/create/](http://127.0.0.1:8000/properties/create/)
- **Application Form**: [http://127.0.0.1:8000/properties/<property_id>/apply/](http://127.0.0.1:8000/properties/3/apply/)
- **Logout**: [http://127.0.0.1:8000/logout/](http://127.0.0.1:8000/logout/)

## **Features**

- **Tenant Features**:
  - Browse available properties.
  - Apply for properties with an optional message.
  - Leave reviews for properties.
  - Make payments for approved applications.

- **Landlord Features**:
  - Create new property listings.
  - View and manage applications for their properties (approve/reject).
  - View the status of applications and payments.

- **Admin Panel**:
  - Full access to manage properties, applications, users, and reviews via the Django admin interface.

## **Django Admin**

The Django Admin interface allows the superuser to manage the site’s data.

- **Admin URL**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Login Credentials**: Use the superuser credentials you created with the `createsuperuser` command.

In the admin panel, you can:
- Add or edit properties, rental applications, payments, and reviews.
- Manage users (landlords and tenants).

## **API Endpoints**

The application exposes several REST API endpoints using Django REST Framework (DRF). Below are the key endpoints:

- **Properties**:
  - `GET /api/properties/`: List all properties.
  - `POST /api/properties/`: Create a new property (landlord only).
  - `GET /api/properties/<id>/`: View property details.
  
- **Rental Applications**:
  - `GET /api/applications/`: List all applications.
  - `POST /api/applications/`: Create a new rental application (tenant only).
  - `PATCH /api/applications/<id>/`: Update the status of an application (landlord only).

- **Payments**:
  - `POST /api/payments/`: Make a payment (tenant only).

- **Reviews**:
  - `POST /api/reviews/`: Submit a review for a property (tenant only).

### Authentication:
- The API uses **JWT Authentication** and **Session Authentication**. You can obtain a token using the `POST /api/auth/login/` endpoint.

## **Testing**

To run automated tests, use the following command:


