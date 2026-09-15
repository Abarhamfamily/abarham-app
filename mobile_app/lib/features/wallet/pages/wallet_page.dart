import 'package:flutter/material.dart';

import '../../../core/theme/app_colors.dart';
import '../models/wallet.dart';
import '../models/wallet_transaction.dart';
import '../repositories/api_wallet_repository.dart';

class WalletPage extends StatefulWidget {
  const WalletPage({super.key});

  @override
  State<WalletPage> createState() => _WalletPageState();
}

class _WalletPageState extends State<WalletPage> {
  final ApiWalletRepository _repository = ApiWalletRepository();

  late Future<WalletBalance> _walletFuture;
  late Future<List<WalletTransaction>> _transactionsFuture;

  bool _isCharging = false;
  bool _isWithdrawing = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() {
    _walletFuture = _repository.getWallet();
    _transactionsFuture = _repository.getTransactions();
  }

  void _retry() {
    setState(() {
      _loadData();
    });
  }

  static const Map<String, String> _statusLabels = {
    'pending': 'در انتظار تأیید',
    'confirmed': 'تأیید شده',
    'failed': 'ناموفق',
    'reversed': 'رد شده',
  };

  static const Map<String, String> _typeLabels = {
    'deposit': 'واریز',
    'withdrawal': 'برداشت',
    'credit_usage': 'استفاده از اعتبار',
    'refund': 'بازگشت وجه',
    'gift_credit': 'اعتبار هدیه',
    'fee': 'کارمزد',
    'adjustment': 'تعدیل',
  };

  String _formatPrice(String rawPrice) {
    final isNegative = rawPrice.startsWith('-');
    final unsigned = isNegative ? rawPrice.substring(1) : rawPrice;
    final integerPart = unsigned.split('.').first;
    final groups = <String>[];
    var end = integerPart.length;
    while (end > 0) {
      final start = end > 3 ? end - 3 : 0;
      groups.insert(0, integerPart.substring(start, end));
      end = start;
    }
    final sign = isNegative ? '-' : '';
    return '$sign${groups.join(',')} تومان';
  }

  Future<void> _handleChargePressed() async {
    final amountController = TextEditingController();

    final amount = await showDialog<String>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('شارژ کیف پول'),
          content: TextField(
            controller: amountController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(
              labelText: 'مبلغ (تومان)',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('انصراف'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop(amountController.text.trim());
              },
              child: const Text('پرداخت'),
            ),
          ],
        );
      },
    );

    if (amount == null || amount.isEmpty) return;
    if (!mounted) return;

    setState(() => _isCharging = true);

    try {
      final chargeResponse = await _repository.chargeWallet(amount: amount);
      final verifyResponse = await _repository.verifyCharge(
        transactionId: chargeResponse.transactionId,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(verifyResponse.message)),
      );

      if (verifyResponse.success) {
        setState(() {
          _loadData();
        });
      }
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isCharging = false);
      }
    }
  }

  Future<void> _handleWithdrawPressed() async {
    final amountController = TextEditingController();
    final cardController = TextEditingController();

    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('درخواست برداشت'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: amountController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'مبلغ (تومان)',
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: cardController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'شماره کارت',
                ),
              ),
              const SizedBox(height: 8),
              const Align(
                alignment: Alignment.centerRight,
                child: Text(
                  'شما تنها می‌توانید تا ۸۰٪ موجودی خود را برداشت کنید',
                  style: TextStyle(fontSize: 11, color: Color(0xFF718078)),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('انصراف'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pop({
                  'amount': amountController.text.trim(),
                  'cardNumber': cardController.text.trim(),
                });
              },
              child: const Text('ثبت درخواست'),
            ),
          ],
        );
      },
    );

    if (result == null || result['amount']!.isEmpty || result['cardNumber']!.isEmpty) {
      return;
    }
    if (!mounted) return;

    setState(() => _isWithdrawing = true);

    try {
      await _repository.requestWithdrawal(
        amount: result['amount']!,
        cardNumber: result['cardNumber']!,
      );

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('درخواست برداشت شما ثبت شد و در انتظار تأیید است')),
      );

      setState(() {
        _loadData();
      });
    } catch (e) {
      if (!mounted) return;
      final message = e.toString().replaceFirst('Exception: ', '');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(message)),
      );
    } finally {
      if (mounted) {
        setState(() => _isWithdrawing = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('کیف پول من'),
        ),
        body: RefreshIndicator(
          onRefresh: () async {
            setState(() {
              _loadData();
            });
          },
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              FutureBuilder<WalletBalance>(
                future: _walletFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState != ConnectionState.done) {
                    return const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24),
                      child: Center(child: CircularProgressIndicator()),
                    );
                  }

                  if (snapshot.hasError) {
                    return Column(
                      children: [
                        const Text('دریافت موجودی با خطا مواجه شد'),
                        const SizedBox(height: 12),
                        ElevatedButton(
                          onPressed: _retry,
                          child: const Text('تلاش مجدد'),
                        ),
                      ],
                    );
                  }

                  final wallet = snapshot.data!;
                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [
                          AppColors.primary,
                          Color(0xFF9DBB73),
                        ],
                        begin: Alignment.topRight,
                        end: Alignment.bottomLeft,
                      ),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'موجودی فعلی',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          _formatPrice(wallet.balance),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (_isPositiveAmount(wallet.pendingBalance)) ...[
                          const SizedBox(height: 4),
                          Text(
                            'در انتظار تسویه: ${_formatPrice(wallet.pendingBalance)}',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 11,
                            ),
                          ),
                        ],
                        const SizedBox(height: 16),
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _isCharging ? null : _handleChargePressed,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.white,
                                  foregroundColor: AppColors.primary,
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                ),
                                child: _isCharging
                                    ? const SizedBox(
                                        height: 18,
                                        width: 18,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Text(
                                        'شارژ کیف پول',
                                        style: TextStyle(fontWeight: FontWeight.bold),
                                      ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: ElevatedButton(
                                onPressed: _isWithdrawing ? null : _handleWithdrawPressed,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.white.withValues(alpha: .2),
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(12),
                                    side: const BorderSide(color: Colors.white),
                                  ),
                                ),
                                child: _isWithdrawing
                                    ? const SizedBox(
                                        height: 18,
                                        width: 18,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                          color: Colors.white,
                                        ),
                                      )
                                    : const Text(
                                        'درخواست برداشت',
                                        style: TextStyle(fontWeight: FontWeight.bold),
                                      ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  );
                },
              ),
              const SizedBox(height: 24),
              const Text(
                'تاریخچه تراکنش‌ها',
                style: TextStyle(
                  color: AppColors.foreground,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              FutureBuilder<List<WalletTransaction>>(
                future: _transactionsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState != ConnectionState.done) {
                    return const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24),
                      child: Center(child: CircularProgressIndicator()),
                    );
                  }

                  if (snapshot.hasError) {
                    return const Text('دریافت تراکنش‌ها با خطا مواجه شد');
                  }

                  final transactions = snapshot.data ?? const <WalletTransaction>[];
                  if (transactions.isEmpty) {
                    return const Text('هنوز هیچ تراکنشی ثبت نشده است');
                  }

                  return Column(
                    children: transactions.map((tx) {
                      return Container(
                        margin: const EdgeInsets.only(bottom: 10),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(color: const Color(0xFFE5E4DC)),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _typeLabels[tx.type] ?? tx.type,
                                    style: const TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.bold,
                                      color: AppColors.foreground,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    _statusLabels[tx.status] ?? tx.status,
                                    style: const TextStyle(
                                      fontSize: 11,
                                      color: Color(0xFF718078),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            Text(
                              _formatPrice(tx.amount),
                              style: const TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: AppColors.foreground,
                              ),
                            ),
                          ],
                        ),
                      );
                    }).toList(),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

bool _isPositiveAmount(String value) {
  final trimmed = value.trim();
  if (trimmed.isEmpty) return false;
  final asDouble = double.tryParse(trimmed) ?? 0;
  return asDouble > 0;
}