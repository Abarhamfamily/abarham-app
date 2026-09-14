import 'wallet.dart';

class WalletChargeVerifyResponse {
  final bool success;
  final String message;
  final WalletBalance? wallet;

  const WalletChargeVerifyResponse({
    required this.success,
    required this.message,
    this.wallet,
  });

  factory WalletChargeVerifyResponse.fromJson(Map<String, dynamic> json) {
    return WalletChargeVerifyResponse(
      success: json['success'] as bool,
      message: json['message'] as String,
      wallet: json['wallet'] != null
          ? WalletBalance.fromJson(json['wallet'] as Map<String, dynamic>)
          : null,
    );
  }
}