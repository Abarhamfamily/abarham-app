class Trip {
  final String id;
  final String title;
  final String destination;
  final String? description;
  final DateTime startDate;
  final DateTime endDate;
  final String price;
  final String depositAmount;
  final int capacity;
  final int remainingCapacity;
  final String status;
  final String? transportationType;
  final String? difficultyLevel;
  final String? meetingPoint;
  final String? departureTime;

  const Trip({
    required this.id,
    required this.title,
    required this.destination,
    this.description,
    required this.startDate,
    required this.endDate,
    required this.price,
    required this.depositAmount,
    required this.capacity,
    required this.remainingCapacity,
    required this.status,
    this.transportationType,
    this.difficultyLevel,
    this.meetingPoint,
    this.departureTime,
  });
}
