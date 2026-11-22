# C# / .NET / Blazor Practices

Detail for the "References" pointer in `skill.md`. These cover topics not
already owned by another installed skill. For async patterns, EF Core, unit
testing frameworks, minimal API/OpenAPI conventions, and XML doc comment
conventions, use the csharp-async, efcore-mssql, dotnet-testing,
aspnet-minimal-api-openapi, and csharp-docs skills instead of this file. The
installed `dotnet-best-practices` skill already covers the baseline
"constructor-inject, register sane lifetimes, use `ILogger` structured
logging" rules — this file adds only the sharper, Blazor/options-pattern-
specific detail those generic rules don't go into.

## Naming
- **PascalCase** — types, methods, properties, events, public fields, namespaces.
- **camelCase** — local variables and method parameters.
- **_camelCase** (leading underscore) — private instance fields.
- Interfaces prefixed with `I` (e.g. `IUserRepository`).

## Blazor components
- Default to code-behind: `Dashboard.razor` pairs with `Dashboard.razor.cs`.
- Add `Dashboard.razor.css` (scoped CSS) **only** when the component has its own styling.
- Add `Dashboard.razor.js` (collocated JS module) **only** when the component needs JS interop.
- Do not create empty `.js`/`.css` files for components that don't need them.
- Be explicit about render-mode (Server/WASM/Auto) implications for state —
  don't assume a WASM-only pattern applies to Server, or vice versa.

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

- Default service lifetimes: `Scoped` for services holding per-request/
  per-circuit state; `Transient` for cheap, stateless services; `Singleton`
  only for genuinely stateless or thread-safe shared services (e.g., an
  `IMemoryCache` wrapper). For `DbContext` lifetime specifically, see
  `efcore-mssql` — don't inject a scoped `DbContext` directly and reuse it
  across awaits/renders.
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

`dotnet-best-practices` already requires structured `ILogger` logging; the
exact template syntax and the two rules it doesn't cover:

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
