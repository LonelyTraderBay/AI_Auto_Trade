# Security Policy — AI Auto Trade

## Báo cáo lỗ hổng

Đây là repository riêng tư một chủ sở hữu. Mọi phát hiện bảo mật (lộ secret, lỗ hổng thiết kế, dependency có CVE, sai lệch access control) báo cáo trực tiếp cho **Account Owner** qua kênh riêng tư — không mở public issue, không ghi chi tiết khai thác vào commit message hay tài liệu công khai trong repo.

Khi báo cáo, cung cấp: mô tả, phạm vi ảnh hưởng (file/contract/flow), bước tái hiện nếu có, và đề xuất khắc phục. Người báo cáo không tự sửa các thành phần safety/security/live — theo RACI, thay đổi loại này cần ADR và approver đúng vai trò ([docs/governance/raci.md](docs/governance/raci.md), master §1.6).

## Quy tắc secret — không ngoại lệ

- **Không bao giờ** commit secret, API key, token, credential, private key, `.env` thật, database dump hay log chưa redaction. Quy tắc chi tiết: [docs/backend/security-ops/secrets-and-key-management.md](docs/backend/security-ops/secrets-and-key-management.md).
- Config chỉ chứa `secret_ref`/path tham chiếu — không bao giờ chứa giá trị secret.
- Trade key luôn ở chế độ **không có quyền withdrawal**; credential tách theo environment/account (master §6.1, §12.1).
- BYOK AI key chỉ đi qua secret ingress write-only, không read-back, không log (ADR-0016, SEC-AI-POL-001).
- Nếu một secret đã lỡ vào Git: coi như đã lộ — thu hồi/xoay vòng ngay theo [runbook credential-rotation](docs/backend/security-ops/runbooks/credential-rotation.md), rồi mới xử lý lịch sử Git.

## Tài liệu bảo mật chính

| Chủ đề | Tài liệu |
|---|---|
| Threat model | [docs/backend/security-ops/threat-model.md](docs/backend/security-ops/threat-model.md) |
| Access control / RBAC | [docs/backend/security-ops/access-control-matrix.md](docs/backend/security-ops/access-control-matrix.md) |
| Auth/session | [docs/backend/security-ops/auth-session-policy.md](docs/backend/security-ops/auth-session-policy.md) |
| Secrets/key management | [docs/backend/security-ops/secrets-and-key-management.md](docs/backend/security-ops/secrets-and-key-management.md) |
| Incident runbooks | [docs/backend/security-ops/runbook-index.md](docs/backend/security-ops/runbook-index.md) |
| AI BYOK security | [docs/backend/security-ops/ai-byok-security-policy.md](docs/backend/security-ops/ai-byok-security-policy.md) |

## Phạm vi hiện tại

Repo đang ở Phase 0.0 (docs-only): chưa có runtime, endpoint, credential hay hạ tầng thật. Bề mặt tấn công hiện tại là chuỗi cung ứng tài liệu/contract và quy trình approval — vì vậy mọi thay đổi safety/security đều yêu cầu approver độc lập theo RACI, kể cả trong giai đoạn tài liệu.
