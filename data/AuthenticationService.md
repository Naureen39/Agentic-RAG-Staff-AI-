# Authentication Service

The Authentication Service manages all user identity-related operations such as login, signup, and token generation.

## Responsibilities
- Validate user credentials
- Generate and verify JWT tokens
- Register new users
- Reset passwords
- Validate user profiles

## Modules
1. LoginModule
2. SignupModule
3. TokenGenerator
4. UserProfileValidator

## Dependencies
- UserService
- EmailService
- NotificationService

## Used By
- PaymentService
- BillingService
- ProjectABackend
