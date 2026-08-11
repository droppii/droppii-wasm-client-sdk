# Nhật ký đồng bộ Core → JS SDK

## Sync 2026-08-11 — Core dev đến PR#47 (`ce755413`)

Core `dev` tiến từ PR#45 (`bd1e1dfa`) lên PR#47 (`ce755413`) — 2 PR mới.

Đã port 2 PR Core sang JS SDK:

| PR Core | Branch | Thay đổi | Bổ sung ở JS SDK |
|---|---|---|---|
| [#46](https://github.com/droppii/openimsdk-core/pull/46) | feat/DROPPII-30105(grant-admin-role) | Fix nil-safety `StringArray.Value()`/`Scan()` (không đổi shape); thêm fallback `DefaultPermissions(roleLevel)` khi server không trả `Permissions`; thêm 11 permission-key string constant (`protocol/constant/group_permission.go`) | Enum `GroupPermission` (DX, không bắt buộc kỹ thuật — field `permissions` đã đúng type `string[]` từ PR#45); đổi `permissions` trên `GroupMemberItem`/`SelfUserInfo` sang `GroupPermission[]` |
| [#47](https://github.com/droppii/openimsdk-core/pull/47) | feat/DROPPII-30296(search-public-group) | Export mới `SearchPublicGroups` (`wasm/cmd/main.go`, `wasm/wasm_wrapper/wasm_group.go`) | `searchPublicGroups()`, enum `PublicGroupJoinStatus`, type `SearchPublicGroupsParams`/`SearchPublicGroupInfo`/`SearchPublicGroupMemberInfo`/`SearchPublicGroupsResult` |

Gộp PR#46+#47 vào 1 commit vì PR#46 chỉ đổi type của field đã port (không có shape mới độc lập) và cả 2 PR đụng chung nhiều hunk trong cùng file.

### Fix bổ sung — gap SQL schema cho `permissions` (giống lỗi `visibility` tuần trước)

Trong lúc audit, phát hiện `permissions` (port ở PR#45 tuần trước, dùng cho `LocalGroupMember`/`LocalUser`) có cùng loại gap với `visibility`: SQL schema `local_group_members`/`local_users` (`src/sqls/`) chưa có cột `permissions`, và `alter.ts` chưa có migration. Nghiêm trọng hơn: field `permissions` là **array**, và test trực tiếp xác nhận `squel.setFields()` **throw lỗi cứng** khi gặp giá trị array (`"field value must be a string, number, boolean, null or one of the registered custom value types"`) — nghĩa là bất kỳ insert/update `LocalGroupMember`/`LocalUser` nào có `permissions` sẽ crash runtime, không chỉ thiếu cột.

Đã thêm cột `permissions TEXT` vào schema + migration `alter021`, và helper `serializeArrayFields`/`deserializeArrayFields` (`src/utils/value.ts`) áp dụng tại toàn bộ 4 điểm insert/update và 11 điểm select liên quan trong `groupMember.ts`/`users.ts` — JSON-stringify trước khi insert, JSON-parse khi đọc ra.

Version package: `0.2.1` → `0.3.0` (minor — bổ sung method/type mới `searchPublicGroups`).

## Fix 2026-08-10 — Bổ sung cột `visibility` vào SQL schema `local_groups` (thiếu ở sync PR#44)

Sync `a104f64` (mục "Sync 2026-08-08" bên dưới) port field `visibility` cho PR#44 nhưng chỉ cập nhật type TypeScript (`GroupVisibility` enum, `GroupItem.visibility`) — không cập nhật SQL schema thật của `local_groups` trong `src/sqls/localGroups.ts` (thiếu cột trong `CREATE TABLE`) và `src/api/database/alter.ts` (thiếu `ALTER TABLE` migration cho DB đã tồn tại từ trước). Hậu quả: mọi `insertGroup`/`updateGroup` chứa field `visibility` (đến từ Core WASM qua `wasm/indexdb/group_model.go`) throw lỗi runtime `table local_groups has no column named visibility` trên cả DB mới và DB cũ.

**Đã fix:**
- `src/sqls/localGroups.ts`: thêm cột `'visibility' INTEGER` vào `CREATE TABLE IF NOT EXISTS local_groups`.
- `src/api/database/alter.ts`: thêm `alter383()` — `ALTER TABLE local_groups ADD COLUMN visibility INTEGER;` (đặt tên theo version Core hiện tại `3.8.3`, theo convention `alter351`/`alter380` đã có), gọi trong `alterTable()` cho user có DB cũ từ trước sync PR#44.

Version package: `0.2.0` → `0.2.1` (patch — fix schema, không đổi API/type).

## Sync 2026-08-08 — Core dev đến PR#45 (`bd1e1dfa`)

Core `dev` tiến từ PR#42 (`902c93f1`) lên PR#45 (`bd1e1dfa`) — 2 PR mới, cả 2 đều cần port.

Đã port 2 PR Core sang JS SDK:

| PR Core | Branch | Thay đổi | Bổ sung ở JS SDK |
|---|---|---|---|
| [#44](https://github.com/droppii/openimsdk-core/pull/44) | feat/DROPPII-29975(Livechat-CRM-Group-Create-group) | Thêm field `Visibility int32` vào `LocalGroup` (`pkg/db/model_struct/data_model_struct.go`, dùng trực tiếp trong `wasm/indexdb/group_model.go`); hằng số `GroupVisibilityPrivate=0`/`GroupVisibilityPublic=1` | Enum `GroupVisibility`, field `visibility?: GroupVisibility` trên `GroupItem` |
| [#45](https://github.com/droppii/openimsdk-core/pull/45) | feat/create-group-and-permission | (a) Thêm field `Permissions StringArray` vào `LocalGroupMember` và `LocalUser` (dùng trực tiếp trong `wasm/indexdb/`); (b) đổi signature `open_im_sdk.GetSelfUserInfo(callback, operationID)` → `(callback, operationID, groupID)` — hàm này được `wasm_wrapper.GetSelfUserInfo` gọi trực tiếp qua reflection (`wasm/event_listener/caller.go`), khi `groupID` không rỗng Core trả kèm quyền (`permissions`) của user trong group đó | Field `permissions?: string[]` trên `GroupMemberItem`/`SelfUserInfo`; **breaking**: `getSelfUserInfo()` đổi từ `(operationID?)` → `(operationID?, groupID?)` — theo quyết định người dùng, đặt `operationID` trước để khớp đúng thứ tự tham số Go (`open_im_sdk.GetSelfUserInfo(callback, operationID, groupID)`), phá vỡ convention "operationID luôn ở cuối" của các method khác trong SDK; callers đang gọi `getSelfUserInfo(myOpId)` vẫn tương thích (groupID mặc định `''`), callers cần truyền groupID sửa lại thành `getSelfUserInfo(myOpId, groupId)` |

### Ghi chú kỹ thuật quan trọng — cơ chế đệm tham số của wasm caller

Không phải mọi thay đổi Core cần export `js.Global().Set(...)` mới mới đáng port. `PR#44`/`#45` không thêm export nào — chỉ thêm field vào struct Go dùng chung qua nhiều wasm export sẵn có (`LocalGroup`, `LocalGroupMember`, `LocalUser`), và đổi signature 1 hàm hiện có. Xác nhận qua `wasm/event_listener/caller.go` (dòng ~91-93): reflection tự đệm thêm 1 `js.Value{}` rỗng nếu số tham số Go nhiều hơn số args JS truyền đúng 1 — nên các JS call cũ (thiếu `groupID`) không crash runtime (Go nhận `groupID=""`), nhưng vẫn cần port để expose khả năng truyền `groupID` thật.

Version package: `0.1.4` → `0.2.0` (minor — breaking change ở `getSelfUserInfo()`).

## Fix 2026-07-30 (3) — Publish fix `MessageItem` (bổ sung `isPinned`/`pinnedByUserID`/`pinnedTime`)

PR #6 (thêm 3 field pin vào `MessageItem`, xem mục "Fix 2026-07-30 (2)" bên dưới — mục lộn giữa PR#5/PR#6, xem git log để đối chiếu chính xác) merge **sau** khi workflow publish `0.1.3` đã chạy xong (`0.1.3` publish tại commit `1bf8144`, PR#6 merge tại `3cee6c6`) — nên `0.1.3` trên npm chưa có field `pinnedTime`, dù đã merge vào `main`.

Version package: `0.1.3` → `0.1.4` (patch — chỉ để trigger publish, không có thay đổi code mới ngoài field đã merge ở PR#6).

## Fix 2026-07-30 (2) — Gộp lại `GetAdvancedHistoryMsgParams` cho cả 4 method

Fix `0.1.2` (bên dưới) chỉ sửa 2 method App bằng cách tách type riêng `GetAdvancedHistoryMsgAppParams`, nhưng 2 method non-App (`getAdvancedHistoryMessageList`/`getAdvancedHistoryMessageListReverse`) vẫn giữ `GetAdvancedHistoryMsgParams` cũ có `lastMinSeq`/`userID`/`groupID`.

Xác nhận lại: cả 4 wasm export (`GetAdvancedHistoryMessageList`, `GetAdvancedHistoryMessageListReverse`, `GetAdvancedHistoryMessageListApp`, `GetAdvancedHistoryMessageListReverseApp`) đều nhận **cùng 1** struct Go (`pkg/sdk_params_callback/conversation_msg_sdk_struct.go`, `GetAdvancedHistoryMessageListParams` — chỉ `conversationID`, `startClientMsgID`, `count`, `viewType`). Vậy `lastMinSeq`/`userID`/`groupID` chưa từng đúng cho bất kỳ method nào trong 4 method này, kể cả 2 method non-App có từ trước khi skill sync này tồn tại.

**Đã fix:** gộp `GetAdvancedHistoryMsgAppParams` vào lại `GetAdvancedHistoryMsgParams` (xoá field thừa, giữ đúng theo Go struct), dùng chung cho cả 4 method thay vì tách 2 type trùng lặp.

**Lưu ý cho consumer:** nếu code cũ có truyền `lastMinSeq`/`userID`/`groupID` vào bất kỳ method nào trong 4 method trên, cần bỏ các field đó (compile-time only — Go đã âm thầm bỏ qua field thừa từ trước giờ nên hành vi runtime không đổi).

Version package: `0.1.2` → `0.1.3` (patch).

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
