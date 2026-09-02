# Documentation Requirements

Detail for the "Documentation requirements" rule in `skill.md`. Applies whenever
this skill's "Use this skill when" triggers apply.

## API developer documentation

Any time you add or change a public API surface — a minimal API endpoint, a
controller action, or a public method/class other code depends on — do both
of the following:

1. **XML doc comments** on the public surface: `<summary>`, `<param>`,
   `<returns>`, and `<exception>` tags as applicable. Follow the conventions
   in the csharp-docs skill.
2. **OpenAPI/Swagger annotations** kept current: `.WithSummary()`,
   `.WithDescription()`, `.Produces<T>()` for minimal APIs, or
   `[ProducesResponseType]` / `[SwaggerOperation]` for controllers. Follow
   the conventions in the aspnet-minimal-api-openapi skill.

Do this in the same change that adds or modifies the API — not as a follow-up.

Example (minimal API):

```csharp
/// <summary>Retrieves a customer by id.</summary>
/// <param name="id">The customer's unique identifier.</param>
/// <returns>The matching customer, or 404 if not found.</returns>
app.MapGet("/customers/{id}", (int id, ICustomerRepository repo) =>
{
    var customer = repo.GetById(id);
    return customer is not null ? Results.Ok(customer) : Results.NotFound();
})
.WithSummary("Get a customer by id")
.WithDescription("Retrieves a single customer record by its unique identifier.")
.Produces<Customer>(StatusCodes.Status200OK)
.Produces(StatusCodes.Status404NotFound);
```

## Node/TypeScript API documentation

Any time you add or change a public API surface in a Node/TypeScript
project — an exported function/class other code depends on, or an HTTP
route — do both of the following:

1. **JSDoc/TSDoc comments** on the exported surface: a summary line plus
   `@param`, `@returns`, and `@throws` tags as applicable.
2. **OpenAPI/Swagger annotations kept current**, using whatever the
   project's framework already provides (e.g. the NestJS Swagger module,
   `tsoa` decorators, `zod-to-openapi` schemas). Don't introduce a second
   OpenAPI toolchain alongside an existing one.

```typescript
/**
 * Retrieves a customer by id.
 * @param id - The customer's unique identifier.
 * @returns The matching customer.
 * @throws {NotFoundError} If no customer has that id.
 */
export async function getCustomer(id: string): Promise<Customer> {
  // ...
}
```

## Python API documentation

Any time you add or change a public API surface in a Python project — a
public function/method/class other code depends on, or an HTTP route —
do both of the following:

1. **Docstrings with type hints** on the public surface, following the
   conventions in `references/python-practices.md`.
2. **OpenAPI/Swagger annotations kept current**, using whatever the
   project's framework already provides (e.g. FastAPI's automatic docs
   generated from type hints and Pydantic models, `flask-smorest`,
   `drf-yasg`). Don't introduce a second OpenAPI toolchain alongside an
   existing one.

## Web application user documentation

Any time you add or change a user-facing page or feature — a Blazor page,
a React page/component, or any other UI — add or update a markdown file
describing it for end users:

- **Location:** `docs/user/<feature-name>.md` (one file per feature/page;
  kebab-case filename matching the feature).
- **Audience:** end users, not developers — describe what the feature does
  and how to use it, not implementation details.
- **Template:**

```markdown
# <Feature Name>

## What it does

<1-3 sentences describing the feature's purpose.>

## How to use it

<Step-by-step instructions a user would follow.>

## Notes

<Any gotchas, limitations, or things that commonly confuse users. Omit this
section if there are none.>
```

- **When to create vs. update:** create a new file the first time a
  user-facing feature is added; update the existing file (don't create a
  second one) when that feature changes in a way that affects how a user
  interacts with it. Cosmetic-only changes (styling, layout tweaks that don't
  change behavior) don't require a doc update.
