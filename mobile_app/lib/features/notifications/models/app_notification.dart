class AppNotification {
  final String id;
  final String type;
  final String title;
  final String content;
  final Map<String, dynamic>? data;
  final String? readAt;
  final String sentAt;

  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.content,
    this.data,
    this.readAt,
    required this.sentAt,
  });

  bool get isRead => readAt != null;

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      content: json['content'] as String,
      data: json['data'] as Map<String, dynamic>?,
      readAt: json['read_at'] as String?,
      sentAt: json['sent_at'] as String,
    );
  }
}