class WalletChargeResponse {
  final String transactionId;
  final String paymentUrl;
  final String authority;

  const WalletChargeResponse({
    required this.transactionId,
    required this.paymentUrl,
    required this.authority,
  });

  factory WalletChargeResponse.fromJson(Map<String, dynamic> json) {
    return WalletChargeResponse(
      transactionId: json['transaction_id'] as String,
      paymentUrl: json['payment_url'] as String,
      authority: json['authority'] as String,
    );
  }
}