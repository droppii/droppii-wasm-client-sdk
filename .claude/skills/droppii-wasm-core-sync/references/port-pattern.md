# Port Pattern: Core Go Export → JS SDK Method

Every Core `wasm/` export that needs a JS-side port touches the same 4 files, in this order. Use `createUrlTextMessage` (already in the codebase) as the worked example for a message-creation method; adapt the shape for non-message methods (e.g. list/pin/get methods skip the enum step).

## 1. `src/types/enum.ts` — only for new message content types

If the Core PR adds a new message content type (like `createStickerMessage`, `createButtonMessage`), add a value to the `MessageType` enum matching the Go-side content type constant exactly:

```typescript
export enum MessageType {
  // ...
  UrlTextMessage = 160,
  LogTextMessage = 161,
  // new: StickerMessage = 162,  <- must match Core's constant.StickerMessage value
}
```

Find the Go-side constant in Core's `constant/` package (search for the content-type int the PR introduces) — do not invent the number, copy it from Go source.

Skip this file entirely for non-message-type ports (list/get/pin methods, schema field additions).

## 2. `src/types/entity.ts` — element/type shape

For a new message element type, add the `*Elem` type and reference it from `MessageItem`:

```typescript
// added to MessageItem:
urlTextElem?: UrlTextElem;

// new type:
export type UrlTextElem = {
  content: string;
  urls: string[];
};
```

Field names and types must match the Go struct's JSON tags exactly (`json:"content"`, `json:"urls"`, etc.) — read the actual Go struct definition, don't infer from the export function's Go parameter names.

For schema/field-addition PRs (e.g. adding `MaxSeq`/`MinSeq` to `LocalConversation`), add the corresponding camelCase fields to the relevant entity type (e.g. `ConversationItem`) instead of a new `*Elem` type.

## 3. `src/types/index.d.ts` — `window.*` global declaration

Every Core export registered via `js.Global().Set("methodName", ...)` needs a matching ambient declaration under the `// registered by go wasm` section:

```typescript
createUrlTextMessage: (
  operationID: string,
  text: string,
  urls: string
) => Promise<string[]>;
```

Rules:
- First param is always `operationID: string`.
- Remaining params match the Go wasm_wrapper function signature, in order, as their JS-serializable equivalents (Go `string` → TS `string`, Go struct param passed as JSON → TS `string` since it's `JSON.stringify`'d by the caller).
- Return type is the literal shape the Go side resolves the JS Promise with — check `wasm_wrapper` for whether it resolves with a raw string, an array of strings, or an object; message-creation methods typically resolve `Promise<string[]>` (JSON-encoded item wrapped in an array for legacy compat), other methods often resolve `Promise<string>` (a single JSON-encoded payload).

## 4. `src/sdk/index.ts` — the `_invoker`-wrapped SDK method

```typescript
createUrlTextMessage = (
  text: string,
  urls: string,
  operationID = uuidv4()
) => {
  return this._invoker<MessageItem>(
    'createUrlTextMessage',
    window.createUrlTextMessage,
    [operationID, text, urls],
    data => {
      // compitable with old version sdk
      return data[0];
    }
  );
};
```

Rules:
- Public method params come first (in the same order as the Go signature, minus `operationID`), `operationID = uuidv4()` last, always defaulted.
- `_invoker<T>` generic `T` is the return type consumers will get back (e.g. `MessageItem`, `ConversationItem[]`, `GroupMemberItem[]`) — match to whichever entity type Step 2 introduced or reused.
- The 3rd arg is the raw call-args array — must match the `window.*` declaration's positional args from Step 3.
- The optional 4th arg is a transform callback applied to whatever the wasm call resolves with. Only needed if the raw resolved value needs reshaping (e.g. unwrapping `data[0]` for legacy array-wrapped single-item responses) — omit it if the raw shape is already what should be returned.

## Non-message-type example shape (list/get methods)

For methods like `getConversationListSplitApp` or `getAdvancedHistoryMessageListApp` (no new enum, no new `*Elem`, just a new paginated getter): skip Step 1 and Step 2's `*Elem` type (reuse or add fields to an existing entity type if the response shape needs it), then do Step 3 + Step 4 following the closest existing analogous method (e.g. model `getConversationListSplitApp` directly on the non-"App" `getConversationList`/similar existing paginated getter already in `src/sdk/index.ts`, changing only the window binding name and params to match the new Go function's actual signature).

## Verification after every port

```bash
npm run typecheck
npm run lint
```

Fix errors before committing — do not commit a port with type errors, and do not silence typecheck/lint failures.
