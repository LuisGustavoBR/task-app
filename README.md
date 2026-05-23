# Task App

## About

`Task App` is a small personal task creation web application built as a hands-on project for learning and applying modern DevOps and DevSecOps practices. It demonstrates a practical implementation of a Python-based service with containerization, database migrations, authentication, and secure development workflows.

## Purpose

This repository was created for:

- personal use and experimentation
- practicing market-standard DevOps workflows
- applying DevSecOps principles in a lightweight application

## Key Features

- Python web application with authentication and task management
- Database migrations managed with Alembic
- Container-ready setup for Docker and Kubernetes workflows
- Focus on secure development and operational best practices

## Goals

The main goal is to serve as a personal sandbox for building, securing, and deploying a real application using industry best practices. It is not intended as a production product, but as a learning and experimentation platform for DevOps and DevSecOps.

## Structure

The repository includes:

- `main.py` and `routers/` for application logic and routing
- `models.py`, `schemas.py`, and `database.py` for data models and persistence
- `alembic/` for database schema versioning
- `Dockerfile` and `docker-compose.yml` for container-based development
- `static/` and `templates/` for the user interface

## Notes

This project is maintained for personal development, learning, and demonstrating how secure and maintainable deployments can be built with modern tooling.