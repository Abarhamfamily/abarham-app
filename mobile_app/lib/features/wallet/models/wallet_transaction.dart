class WalletTransaction {
  final String id;
  final String amount;
  final String type;
  final String status;
  final String? description;
  final String createdAt;

  const WalletTransaction({
    required this.id,
    required this.amount,
    required this.type,
    required this.status,
    this.description,
    required this.createdAt,
  });

  factory WalletTransaction.fromJson(Map<String, dynamic> json) {
    return WalletTransaction(
      id: json['id'] as String,
      amount: json['amount'].toString(),
      type: json['type'] as String,
      status: json['status'] as String,
      description: json['description'] as String?,
      createdAt: json['created_at'] as String,
    );
  }
}