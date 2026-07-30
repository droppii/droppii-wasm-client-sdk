# Nhật ký đồng bộ Core → JS SDK

## Fix 2026-07-30 — Sai type params của `getAdvancedHistoryMessageListApp`/`ReverseApp`

Consumer app báo lỗi TypeScript khi cài `0.1.1`: field `lastMinSeq` bị bắt buộc nhưng không thuộc về request thực tế của 2 method này.

**Nguyên nhân:** khi port PR#30 (`feat/Get-list-msg-app`), 2 method `getAdvancedHistoryMessageListApp`/`getAdvancedHistoryMessageListReverseApp` bị gán nhầm type `GetAdvancedHistoryMsgParams` — type này vốn thuộc về 2 method cũ hơn (`getAdvancedHistoryMessageList`/`getAdvancedHistoryMessageListReverse`, có từ trước khi skill này tồn tại) và có field `lastMinSeq`, `userID`, `groupID`.

Đối chiếu lại Go source (`pkg/sdk_params_callback/conversation_msg_sdk_struct.go`, struct `GetAdvancedHistoryMessageListParams`) — struct này dùng chung cho **cả 4** method (App và non-App), và chỉ có 4 field: `conversationID`, `startClientMsgID`, `count`, `viewType`. Không có `lastMinSeq`/`userID`/`groupID` ở tầng Go nào cả — `lastMinSeq` là biến nội bộ dùng cho continuity-tracking (`message_check.go`), không phải field request.

**Đã fix:** thêm type mới `GetAdvancedHistoryMsgAppParams` (`conversationID`, `startClientMsgID`, `count`, `viewType`) đúng theo Go struct, áp dụng cho 2 method App. 2 method non-App giữ nguyên `GetAdvancedHistoryMsgParams` cũ (không đổi, ngoài phạm vi fix — dù dư field so với Go struct, các field dư bị JSON unmarshal bỏ qua nên không lỗi ở runtime, chỉ khác ở compile-time type).

**Fix bổ sung (cùng version):** `viewType` ban đầu type là `number` trần — nhưng Core có định nghĩa hằng số tên rõ ràng (`pkg/cache/conversation_seq_cache.go`: `ViewHistory = 0`, `ViewSearch = 1`), không phải số tuỳ ý caller chọn. Đã thêm enum `ViewType` (export public qua `src/types/enum.ts`) và đổi field `viewType` trong `GetAdvancedHistoryMsgAppParams` sang dùng enum này thay vì `number`.

Version package: `0.1.1` → `0.1.2` (patch — sửa type bug, không đổi runtime behavior).

## Re-audit 2026-07-29 — Fix field thiếu từ PR#20-22 (Core dev vẫn ở PR#42, `902c93f1`)

Core `dev` HEAD không đổi so với lần sync trước (vẫn PR#42). Đây là audit lại toàn bộ 33 PR đã bị skip (#3–#42 trừ 5 PR đã port), không phải sync PR mới.

Phát hiện 1 gap: field `PeerType` (Go: `pkg/db/model_struct/data_model_struct.go`, `json:"peerType,omitempty"`) được thêm vào struct `LocalConversation` từ PR#20 (`feat/New-func-GetConversationListSplitApp`), nhưng lúc đó **chưa** có export `js.Global().Set` nào ở `wasm/` — nên đúng theo tiêu chí "touches wasm/" của audit, PR#20-22 bị skip hợp lý ở lần trước. Export thực tế (`getConversationListSplitApp`) chỉ xuất hiện ở PR#27 — PR này đã được port trước đó, nhưng field `peerType` bị bỏ sót khi viết type `ConversationItem`.

**Đã fix:** thêm `peerType?: string` vào `ConversationItem` (`src/types/entity.ts`). Không cần file nào khác (method `getConversationListSplitApp()` và type đã tồn tại sẵn từ lần port PR#27).

Đã re-diff toàn bộ 33 PR còn lại (#3, #5, #6, #8-22, #24-26, #28-29, #32-38, #40-42) trực tiếp từng PR so với parent đầu tiên trên path `wasm/` — không phát hiện thêm gap nào khác. Toàn bộ vẫn đúng như audit trước: không chạm `wasm/`, hoặc field/logic nội bộ không lộ ra JS-facing signature.

Version package: `0.1.0` → `0.1.1` (patch — chỉ bổ sung 1 optional field, không đổi API).

## Sync 2026-07-29 — Core dev đến PR#42 (`902c93f1`)

Nguồn audit: `plans/260729-sync-js-wasm-with-core-dev/plan.md` (audit thủ công PR#3–#42 của Core `dev`, baseline PR#2 `32c543ac`). Core `dev` HEAD tại thời điểm audit đó trùng khớp với HEAD lúc chạy sync này — không có PR mới nào phát sinh thêm.

Đã port 5 PR Core sang JS SDK:

| PR Core | Branch | Thay đổi | Bổ sung ở JS SDK |
|---|---|---|---|
| [#23](https://github.com/droppii/openimsdk-core/pull/23) | feat/Func-createMergeMsg | Thêm field `MaxSeq`/`MinSeq` vào `temp_struct.LocalConversation` (wasm/indexdb) | `maxSeq`/`minSeq` trên `ConversationItem` (`src/types/entity.ts`) |
| [#27](https://github.com/droppii/openimsdk-core/pull/27) | feat/new-func-get-conversation-list-app | Export mới `GetConversationListSplitApp` | `getConversationListSplitApp()`, type `SplitConversationAppParams` |
| [#30](https://github.com/droppii/openimsdk-core/pull/30) | feat/Get-list-msg-app | Export mới `GetAdvancedHistoryMessageListApp`, `GetAdvancedHistoryMessageListReverseApp` | `getAdvancedHistoryMessageListApp()`, `getAdvancedHistoryMessageListReverseApp()` |
| [#31](https://github.com/droppii/openimsdk-core/pull/31) | feat/pin-msg | Export mới `PinMsg`, `UnpinMsg`, `GetPinnedMsgs`, `GetPinnedMessageList`; event `OnRecvMessagePinned` | `pinMsg()`, `unpinMsg()`, `getPinnedMsgs()`, `getPinnedMessageList()`, `CbEvents.OnRecvMessagePinned`, type `MessagePinnedInfo`/`PinnedMsgInfo`/`GetPinnedMessageListParams`/`GetPinnedMessageListResult` |
| [#39](https://github.com/droppii/openimsdk-core/pull/39) | feat/new-contentType-Sticker-Message | Content-type mới `StickerMessage = 162`, export `CreateStickerMessage` | `MessageType.StickerMessage = 162`, `createStickerMessage()`, type `StickerElem` |

### Đã loại khỏi phạm vi

- **PR#19** (`createButtonMessage`, feat/DROPPII-29011) — `plan.md` audit trước đó liệt kê là "cần port", nhưng đã xác nhận bằng cách đọc trực tiếp lịch sử Core: PR#19 **đã bị revert** trên `dev` (commit `1cd5f0e2`, nằm trong chính khoảng PR mà `plan.md` từng audit nhưng bị bỏ sót). Không còn `ButtonMessage`/`createButtonMessage` ở bất kỳ file Go nào tại Core `dev` HEAD hiện tại — không port.
- **PR#3/8/9** (field `IsInternal`) — theo `plan.md`: thêm rồi revert 2 lần, net effect không đổi. `isInternal` đã có sẵn ở `MessageItem` từ trước, không cần hành động.
- **PR#5** — chỉ sửa nội bộ schema-guard indexdb, không đổi signature JS.
- **29 PR còn lại** (#6, #10-16, #18, #20-22, #24-26, #28-29, #32-38, #40-42) — không chạm `wasm/`, hoặc là các PR chuẩn bị/follow-up nội bộ cho #27/#30/#31 (đã kiểm tra riêng #29, #32 — không đụng `wasm/`).

### Đồng bộ asset — PR#17 (`wasm_exec.js`) và `sql-wasm.wasm`

- **`assets/wasm_exec.js`**: đã copy trực tiếp từ `droppii/openimsdk-core` (`wasm/cmd/static/wasm_exec.js`, Go 1.23 runtime) vào repo này. Trước đó file chỉ có phần đổi tên `go`→`gojs` và harness `_gotest` của PR#17, còn thiếu `O_DIRECTORY` và `globalThis.path.resolve` — giờ đã khớp 100% với Core (diff-verify bằng `diff`, không còn khác biệt).
- **`assets/sql-wasm.wasm`**: đã kiểm tra checksum SHA-256 so với file `dist/sql-wasm.wasm` trong package `@jlongster/sql.js@1.6.7` (đúng version khai báo trong `package.json`) — khớp byte-for-byte, không cần cập nhật. File này không thuộc Core, là artifact của package `sql.js` độc lập.

Version package: `3.8.2-1` → xem commit bump version riêng.
