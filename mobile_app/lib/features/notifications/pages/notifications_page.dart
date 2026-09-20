import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../models/app_notification.dart';
import '../repositories/api_notification_repository.dart';

class NotificationsPage extends StatefulWidget {
  const NotificationsPage({super.key});

  @override
  State<NotificationsPage> createState() => _NotificationsPageState();
}

class _NotificationsPageState extends State<NotificationsPage> {
  final ApiNotificationRepository _repository = ApiNotificationRepository();
  late Future<List<AppNotification>> _future;
  bool _isMarkingAll = false;

  @override
  void initState() {
    super.initState();
    _future = _repository.getNotifications();
  }

  void _retry() {
    setState(() {
      _future = _repository.getNotifications();
    });
  }

  String _formatDate(String rawDate) {
    final date = DateTime.tryParse(rawDate);
    if (date == null) return rawDate;
    final local = date.toLocal();
    final month = local.month.toString().padLeft(2, '0');
    final day = local.day.toString().padLeft(2, '0');
    final hour = local.hour.toString().padLeft(2, '0');
    final minute = local.minute.toString().padLeft(2, '0');
    return '${local.year}/$month/$day  $hour:$minute';
  }

  Future<void> _handleNotificationTap(AppNotification notification) async {
    if (notification.isRead) return;

    try {
      await _repository.markAsRead(notification.id);
      if (!mounted) return;
      setState(() {
        _future = _repository.getNotifications();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    }
  }

  Future<void> _handleMarkAllPressed() async {
    setState(() => _isMarkingAll = true);

    try {
      await _repository.markAllAsRead();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('همه‌ی اعلان‌ها خوانده شد')),
      );
      setState(() {
        _future = _repository.getNotifications();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isMarkingAll = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('اعلان‌ها'),
          actions: [
            TextButton(
              onPressed: _isMarkingAll ? null : _handleMarkAllPressed,
              child: _isMarkingAll
                  ? const SizedBox(
                      height: 16,
                      width: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text(
                      'خواندن همه',
                      style: TextStyle(color: Colors.white),
                    ),
            ),
          ],
        ),
        body: FutureBuilder<List<AppNotification>>(
          future: _future,
          builder: (context, snapshot) {
            if (snapshot.connectionState != ConnectionState.done) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text('دریافت اعلان‌ها با خطا مواجه شد'),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _retry,
                      child: const Text('تلاش مجدد'),
                    ),
                  ],
                ),
              );
            }

            final notifications = snapshot.data ?? const <AppNotification>[];
            if (notifications.isEmpty) {
              return const Center(
                child: Text('اعلانی وجود ندارد'),
              );
            }

            return RefreshIndicator(
              onRefresh: () async {
                setState(() {
                  _future = _repository.getNotifications();
                });
              },
              child: ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: notifications.length,
                separatorBuilder: (_, __) => const SizedBox(height: 10),
                itemBuilder: (context, index) {
                  final n = notifications[index];
                  return GestureDetector(
                    onTap: () => _handleNotificationTap(n),
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: n.isRead ? Colors.white : const Color(0xFFF3F7EE),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(
                          color: n.isRead ? const Color(0xFFE5E4DC) : AppColors.primary,
                        ),
                      ),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (!n.isRead) ...[
                            Container(
                              margin: const EdgeInsets.only(top: 4, left: 8),
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: AppColors.primary,
                                shape: BoxShape.circle,
                              ),
                            ),
                          ],
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  n.title,
                                  style: TextStyle(
                                    fontSize: 14,
                                    fontWeight: n.isRead ? FontWeight.normal : FontWeight.bold,
                                    color: AppColors.foreground,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  n.content,
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF718078),
                                  ),
                                ),
                                const SizedBox(height: 6),
                                Text(
                                  _formatDate(n.sentAt),
                                  style: const TextStyle(
                                    fontSize: 10,
                                    color: Color(0xFFAAB0A6),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            );
          },
        ),
      ),
    );
  }
}