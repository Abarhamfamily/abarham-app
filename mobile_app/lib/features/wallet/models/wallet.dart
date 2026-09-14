class WalletBalance {
  final String balance;
  final String pendingBalance;
  final String totalDeposited;
  final String totalWithdrawn;

  const WalletBalance({
    required this.balance,
    required this.pendingBalance,
    required this.totalDeposited,
    required this.totalWithdrawn,
  });

  factory WalletBalance.fromJson(Map<String, dynamic> json) {
    return WalletBalance(
      balance: json['balance'].toString(),
      pendingBalance: json['pending_balance'].toString(),
      totalDeposited: json['total_deposited'].toString(),
      totalWithdrawn: json['total_withdrawn'].toString(),
    );
  }
}