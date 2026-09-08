import 'package:flutter/material.dart';

class AppRouter {
  AppRouter._();

  static MaterialPageRoute<T> route<T>({
    required WidgetBuilder builder,
    RouteSettings? settings,
  }) {
    return MaterialPageRoute<T>(
      builder: builder,
      settings: settings,
    );
  }
}
