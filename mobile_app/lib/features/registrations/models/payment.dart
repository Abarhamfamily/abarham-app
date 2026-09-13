class Payment {
  final String id;
  final String registrationId;
  final String amount;
  final String type;
  final String status;

  const Payment({
    required this.id,
    required this.registrationId,
    required this.amount,
    required this.type,
    required this.status,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'] as String,
      registrationId: json['registration_id'] as String,
      amount: json['amount'].toString(),
      type: json['type'] as String,
      status: json['status'] as String,
    );
  }
}