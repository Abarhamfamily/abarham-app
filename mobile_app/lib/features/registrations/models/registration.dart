class Registration {
  final String id;
  final String userId;
  final String tripId;
  final String status;
  final String totalPrice;
  final String depositPaid;
  final String remainingAmount;
  final int passengerCount;
  final String? vehicleType;
  final int emptySeatsProvided;
  final String? paymentDeadline;
  final String registeredAt;
  final String? confirmedAt;
  final String? cancelledAt;

  const Registration({
    required this.id,
    required this.userId,
    required this.tripId,
    required this.status,
    required this.totalPrice,
    required this.depositPaid,
    required this.remainingAmount,
    required this.passengerCount,
    this.vehicleType,
    required this.emptySeatsProvided,
    this.paymentDeadline,
    required this.registeredAt,
    this.confirmedAt,
    this.cancelledAt,
  });

  factory Registration.fromJson(Map<String, dynamic> json) {
    return Registration(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      tripId: json['trip_id'] as String,
      status: json['status'] as String,
      totalPrice: json['total_price'].toString(),
      depositPaid: json['deposit_paid'].toString(),
      remainingAmount: json['remaining_amount'].toString(),
      passengerCount: (json['passenger_count'] as num).toInt(),
      vehicleType: json['vehicle_type'] as String?,
      emptySeatsProvided: (json['empty_seats_provided'] as num).toInt(),
      paymentDeadline: json['payment_deadline'] as String?,
      registeredAt: json['registered_at'] as String,
      confirmedAt: json['confirmed_at'] as String?,
      cancelledAt: json['cancelled_at'] as String?,
    );
  }
}