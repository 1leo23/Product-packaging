import 'package:flutter/material.dart';
import 'package:trajectory_app/screens/member_screen.dart';
import 'package:trajectory_app/screens/manager_screen.dart';
import 'package:trajectory_app/screens/signin_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Trajectory',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        scaffoldBackgroundColor: Colors.black,
        brightness: Brightness.dark,
      ),
      home: const SigninScreen(),
      routes: {
        '/managerScreen': (context) => const ManagerScreen(),
        '/memberScreen': (context) => const MemberScreen(),
      },
    );
  }
}
