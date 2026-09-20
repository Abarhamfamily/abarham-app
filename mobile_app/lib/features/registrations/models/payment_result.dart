class PaymentResult {
  final String status;
  final String paymentId;
  final String paymentStatus;

  const PaymentResult({
    required this.status,
    required this.paymentId,
    required this.paymentStatus,
  });

  factory PaymentResult.fromJson(Map<String, dynamic> json) {
    final payment = json['payment'] as Map<String, dynamic>;
    return PaymentResult(
      status: json['status'] as String,
      paymentId: payment['id'] as String,
      paymentStatus: payment['status'] as String,
    );
  }
}