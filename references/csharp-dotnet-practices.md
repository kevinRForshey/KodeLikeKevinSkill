# Additional C# / .NET Practices

Detail for the "Additional .NET/C# practices" pointer in `skill.md`. These
cover topics not already owned by another installed skill. For async
patterns, EF Core, unit testing frameworks, minimal API/OpenAPI conventions,
and XML doc comment conventions, use the csharp-async, efcore-mssql,
dotnet-testing, aspnet-minimal-api-openapi, csharp-docs, and
dotnet-best-practices skills instead of this file.

## Nullable reference types & modern C#

- Enable nullable reference types project-wide (`<Nullable>enable</Nullable>`
  in the `.csproj`, or `#nullable enable` if enabling per-file in a mixed
  codebase).
- Prefer `record` / `record class` for immutable data-carrying types (DTOs,
  value objects) over plain classes with manually written equality.
- Prefer pattern matching and switch expressions over nested `if`/`else`
  chains when branching on a value's shape or type.

```csharp
public record CustomerDto(int Id, string Name, string? Email);

string Describe(Shape shape) => shape switch
{
    Circle c => $"Circle with radius {c.Radius}",
    Rectangle r => $"Rectangle {r.Width}x{r.Height}",
    _ => "Unknown shape"
};
```

## Dependency injection & configuration

- Default service lifetimes: `Scoped` for services that use a `DbContext` or
  hold per-request/per-circuit state (this matters especially in Blazor
  Server, where a circuit's scope lives for the connection's lifetime);
  `Transient` for cheap, stateless services; `Singleton` only for genuinely
  stateless or thread-safe shared services (e.g., an `IMemoryCache` wrapper).
- Avoid captive dependencies — never inject a `Scoped` or `Transient`
  service into a `Singleton`.
- Use the options pattern (`IOptions<T>` / `IOptionsSnapshot<T>`) for
  configuration values bound from `appsettings.json`, rather than injecting
  `IConfiguration` directly and reading keys by string throughout the
  codebase.

```csharp
public class EmailOptions
{
    public string SmtpHost { get; set; } = string.Empty;
    public int Port { get; set; }
}

// Program.cs
builder.Services.Configure<EmailOptions>(builder.Configuration.GetSection("Email"));

// Consumer
public class EmailSender(IOptions<EmailOptions> options)
{
    private readonly EmailOptions _options = options.Value;
}
```

## Logging & error handling

- Inject `ILogger<T>` and use structured logging with message templates —
  never string-concatenate or interpolate values directly into the log
  message.

```csharp
// Right
_logger.LogWarning("Order {OrderId} failed validation: {Reason}", orderId, reason);

// Wrong
_logger.LogWarning($"Order {orderId} failed validation: {reason}");
```

- Don't swallow exceptions with an empty `catch` block. Catch only exception
  types you can meaningfully handle; let everything else propagate.
- Handle exceptions at a defined boundary (e.g., middleware for APIs, an
  error boundary component for Blazor UI) rather than scattering try/catch
  through business logic.

## Project/solution layout

- Organize solutions into layered projects reflecting responsibility, e.g.:
  - `<Solution>.Domain` — entities, value objects, domain logic, no
    external dependencies.
  - `<Solution>.Application` — use cases/services, depends on Domain.
  - `<Solution>.Infrastructure` — data access, external integrations,
    implements interfaces defined in Domain/Application.
  - `<Solution>.Web` — Blazor/API host project, depends on the above.
- Align namespaces with folder structure — a type in
  `Infrastructure/Repositories/CustomerRepository.cs` lives in
  `<Solution>.Infrastructure.Repositories`.
