class WaitlistEntry {
  final String id;
  final String userId;
  final String tripId;
  final int position;
  final String status;
  final String? notifiedAt;
  final String createdAt;

  const WaitlistEntry({
    required this.id,
    required this.userId,
    required this.tripId,
    required this.position,
    required this.status,
    this.notifiedAt,
    required this.createdAt,
  });

  factory WaitlistEntry.fromJson(Map<String, dynamic> json) {
    return WaitlistEntry(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      tripId: json['trip_id'] as String,
      position: (json['position'] as num).toInt(),
      status: json['status'] as String,
      notifiedAt: json['notified_at'] as String?,
      createdAt: json['created_at'] as String,
    );
  }
}