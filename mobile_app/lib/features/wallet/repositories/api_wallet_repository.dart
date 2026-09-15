import 'dart:convert';
import '../../../core/constants/api_constants.dart';
import '../../../core/network/api_client.dart';
import '../models/wallet.dart';
import '../models/wallet_transaction.dart';
import '../models/wallet_charge_response.dart';
import '../models/wallet_charge_verify_response.dart';
import 'wallet_repository.dart';

class ApiWalletRepository implements WalletRepository {
  final ApiClient _apiClient;

  ApiWalletRepository({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  @override
  Future<WalletBalance> getWallet() async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/wallet');
    final response = await _apiClient.authenticatedGet(url);

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return WalletBalance.fromJson(data);
      default:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            data['detail'] as String? ?? 'خطا در ارتباط با سرور');
    }
  }

  @override
  Future<List<WalletTransaction>> getTransactions() async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/wallet/transactions');
    final response = await _apiClient.authenticatedGet(url);

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as List<dynamic>;
        return data
            .map((item) => WalletTransaction.fromJson(item as Map<String, dynamic>))
            .toList();
      default:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            data['detail'] as String? ?? 'خطا در دریافت تراکنش‌ها');
    }
  }

  @override
  Future<WalletChargeResponse> chargeWallet({required String amount}) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/wallet/charge');
    final response = await _apiClient.authenticatedPost(
      url,
      body: jsonEncode({'amount': amount}),
    );

    switch (response.statusCode) {
      case 201:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return WalletChargeResponse.fromJson(data);
      default:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            data['detail'] as String? ?? 'خطا در ارتباط با سرور');
    }
  }

  @override
  Future<WalletChargeVerifyResponse> verifyCharge(
      {required String transactionId}) async {
    final url = Uri.parse(
        '${ApiConstants.baseUrl}/api/v1/wallet/charge/$transactionId/verify');
    final response = await _apiClient.authenticatedPost(url);

    switch (response.statusCode) {
      case 200:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return WalletChargeVerifyResponse.fromJson(data);
      default:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            data['detail'] as String? ?? 'خطا در تأیید شارژ');
    }
  }

  @override
  Future<WalletTransaction> requestWithdrawal({
    required String amount,
    required String cardNumber,
  }) async {
    final url = Uri.parse('${ApiConstants.baseUrl}/api/v1/wallet/withdraw');
    final response = await _apiClient.authenticatedPost(
      url,
      body: jsonEncode({'amount': amount, 'card_number': cardNumber}),
    );

    switch (response.statusCode) {
      case 201:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return WalletTransaction.fromJson(data);
      default:
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        throw Exception(
            data['detail'] as String? ?? 'خطا در ثبت درخواست برداشت');
    }
  }
}
