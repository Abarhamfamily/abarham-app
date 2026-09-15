import '../models/wallet.dart';
import '../models/wallet_transaction.dart';
import '../models/wallet_charge_response.dart';
import '../models/wallet_charge_verify_response.dart';

abstract class WalletRepository {
  Future<WalletBalance> getWallet();
  Future<List<WalletTransaction>> getTransactions();
  Future<WalletChargeResponse> chargeWallet({required String amount});
  Future<WalletChargeVerifyResponse> verifyCharge({required String transactionId});
  Future<WalletTransaction> requestWithdrawal({
    required String amount,
    required String cardNumber,
  });
}
