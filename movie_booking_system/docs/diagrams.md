# Design Diagrams

The following Mermaid diagrams can be opened in GitHub, Mermaid Live Editor, or a Markdown editor that supports Mermaid.

## 1. System Architecture

```mermaid
flowchart TD
    U[User / Admin] --> CLI[CLI Interface]
    CLI --> AUTH[Authentication Module]
    CLI --> MOV[Movie & Show Module]
    CLI --> BOOK[Booking Module]
    CLI --> REP[Reports Module]
    AUTH --> DB[(SQLite Database)]
    MOV --> DB
    BOOK --> DB
    REP --> DB
    CLI --> LOG[Application Log]
```

## 2. Workflow Diagram

```mermaid
flowchart TD
    A[Start] --> B{Registered?}
    B -- No --> C[Register]
    B -- Yes --> D[Login]
    C --> D
    D --> E{Valid Login?}
    E -- No --> D
    E -- Yes --> F[Browse Movies]
    F --> G[Choose Movie]
    G --> H[Choose Show]
    H --> I[View Available Seats]
    I --> J[Select Seats]
    J --> K{Seats Available?}
    K -- No --> I
    K -- Yes --> L[Confirm Booking]
    L --> M[Store Booking]
    M --> N[Show Ticket Details]
    N --> O[Booking History / Cancel]
    O --> P[Logout]
    P --> Q[End]
```

## 3. Use Case Diagram

```mermaid
flowchart LR
    C[Customer]
    A[Admin]
    UC1((Register / Login))
    UC2((Browse Movies))
    UC3((Book Tickets))
    UC4((View History))
    UC5((Cancel Booking))
    UC6((Add Movie))
    UC7((Add Show))
    UC8((Delete Movie))
    UC9((View Report))
    C --- UC1
    C --- UC2
    C --- UC3
    C --- UC4
    C --- UC5
    A --- UC1
    A --- UC2
    A --- UC6
    A --- UC7
    A --- UC8
    A --- UC9
```

## 4. Sequence Diagram - Booking

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant MovieService
    participant BookingService
    participant DB
    User->>CLI: Choose movie/show
    CLI->>MovieService: Get show details
    MovieService->>DB: SELECT show
    DB-->>MovieService: Show data
    MovieService-->>CLI: Show data
    User->>CLI: Select seat numbers
    CLI->>BookingService: create_booking()
    BookingService->>DB: Check selected seats
    DB-->>BookingService: Seat status
    BookingService->>DB: INSERT booking + booking_seats
    DB-->>BookingService: Booking saved
    BookingService-->>CLI: Booking details
    CLI-->>User: Confirmation + total price
```

## 5. Class / Component Diagram

```mermaid
classDiagram
    class User {
      +id
      +name
      +email
      +role
    }
    class Movie {
      +id
      +title
      +genre
      +duration
      +language
      +rating
    }
    class Show {
      +id
      +movie_id
      +screen
      +show_date
      +show_time
      +price
    }
    class Booking {
      +id
      +user_id
      +show_id
      +total_amount
      +status
    }
    class AuthService
    class MovieService
    class BookingService
    class ReportService
    User "1" --> "many" Booking
    Movie "1" --> "many" Show
    Show "1" --> "many" Booking
    AuthService --> User
    MovieService --> Movie
    MovieService --> Show
    BookingService --> Booking
    ReportService --> Booking
```

## 6. ER Diagram

```mermaid
erDiagram
    USERS ||--o{ BOOKINGS : makes
    MOVIES ||--o{ SHOWS : has
    SHOWS ||--o{ BOOKINGS : receives
    BOOKINGS ||--o{ BOOKING_SEATS : contains
    SEATS ||--o{ BOOKING_SEATS : assigned

    USERS {
      int id PK
      string name
      string email UK
      string password_hash
      string role
    }
    MOVIES {
      int id PK
      string title
      string genre
      int duration
      string language
      float rating
      string description
    }
    SHOWS {
      int id PK
      int movie_id FK
      string screen
      string show_date
      string show_time
      float price
    }
    SEATS {
      int id PK
      string screen
      string seat_number
    }
    BOOKINGS {
      int id PK
      int user_id FK
      int show_id FK
      float total_amount
      string booked_at
      string status
    }
    BOOKING_SEATS {
      int booking_id PK, FK
      int seat_id PK, FK
    }
```
