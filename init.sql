--- user表
INSERT INTO fastapi_admin.`user`
(id, username, password, email, phone, is_active, created_at, updated_at, deleted_at, token_version)
VALUES(1, 'admin', '$2b$12$LBADLUWYfpP.Z6G3ITRALeoBHo1K0NbGnHmCs1a0PmA0du4hCsFGq', 'admin@qq.com', '1111', 1, '2026-03-29 21:22:23', '2026-04-09 13:58:53', NULL, 1);
INSERT INTO fastapi_admin.`user`
(id, username, password, email, phone, is_active, created_at, updated_at, deleted_at, token_version)
VALUES(2, 'guest', '$2b$12$LBADLUWYfpP.Z6G3ITRALeoBHo1K0NbGnHmCs1a0PmA0du4hCsFGq', 'guest@qq.com', '138888888', 1, '2026-03-29 21:22:23', '2026-03-30 18:30:19', NULL, 0);

--- role表
INSERT INTO fastapi_admin.`role`
(id, code, name, created_at, updated_at, is_active, deleted_at)
VALUES(1, 'admin', '系统管理员', '2026-04-04 09:26:42', '2026-04-04 11:32:14', 1, NULL);
INSERT INTO fastapi_admin.`role`
(id, code, name, created_at, updated_at, is_active, deleted_at)
VALUES(2, 'guest', '访客', '2026-04-04 09:26:42', '2026-04-04 09:27:06', 1, NULL);

--- user_role表
INSERT INTO fastapi_admin.user_role
(user_id, role_id)
VALUES(1, 1);
INSERT INTO fastapi_admin.user_role
(user_id, role_id)
VALUES(1, 2);

--- permission表
INSERT INTO fastapi_admin.permission
(id, code, name, `path`, `method`, created_at, updated_at, deleted_at)
VALUES(1, 'user:add', '添加用户', '/api/private/users', 'POST', '2026-04-08 10:10:14', '2026-04-09 12:59:26', NULL);
INSERT INTO fastapi_admin.permission
(id, code, name, `path`, `method`, created_at, updated_at, deleted_at)
VALUES(2, 'user:update', '修改用户', '/api/private/users', 'PATH', '2026-04-08 10:24:40', '2026-04-09 13:00:01', NULL);
INSERT INTO fastapi_admin.permission
(id, code, name, `path`, `method`, created_at, updated_at, deleted_at)
VALUES(3, 'user:delete', '用户删除', '/api/private/users', 'DELETE', '2026-04-09 10:46:14', '2026-04-09 12:59:53', NULL);
INSERT INTO fastapi_admin.permission
(id, code, name, `path`, `method`, created_at, updated_at, deleted_at)
VALUES(4, 'user:view', '用户查看', '/api/private/users', 'GET', '2026-04-09 10:46:28', '2026-04-09 12:59:53', NULL);

--- role_permission表
INSERT INTO fastapi_admin.role_permission
(role_id, permission_id)
VALUES(1, 1);
INSERT INTO fastapi_admin.role_permission
(role_id, permission_id)
VALUES(1, 2);

--- menu表
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(1, '仪表盘', 'dashboard', 1, NULL, NULL, 0, 1, NULL, NULL, '2026-04-04 11:24:32', '2026-04-09 13:46:32');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(2, '系统管理', 'sys_mgr', 1, NULL, NULL, 1, 1, NULL, NULL, '2026-04-04 11:24:39', '2026-04-09 13:47:16');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(3, '用户管理', 'user_mgr', 2, NULL, NULL, 1, 1, 2, NULL, '2026-04-04 11:24:46', '2026-04-09 13:47:59');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(4, '创建用户', 'user_create', 3, NULL, NULL, 2, 1, 2, 1, '2026-04-04 11:24:53', '2026-04-09 14:01:32');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(5, '修改用户', 'user_update', 3, NULL, NULL, 3, 1, 2, 2, '2026-04-04 11:25:00', '2026-04-09 14:01:32');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(6, '删除用户', 'user_delete', 3, NULL, NULL, 4, 1, 2, 3, '2026-04-09 13:44:20', '2026-04-09 14:01:32');
INSERT INTO fastapi_admin.menu
(id, name, code, `type`, icon, `path`, sort, is_visible, parent_id, permission_id, created_at, updated_at)
VALUES(7, '查看用户', 'user_view', 3, NULL, NULL, 5, 1, 2, 4, '2026-04-09 13:48:42', '2026-04-09 14:01:32');
