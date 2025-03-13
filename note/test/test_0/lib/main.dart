import 'package:flutter/material.dart';

void main() {
  runApp(const MaterialApp(home: LoginPage()));
}

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  TextEditingController emailController = TextEditingController();
  TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text("Header")),
        body: Container(
          margin: EdgeInsets.all(30),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: emailController,
                decoration: InputDecoration(hintText: "Email"),
              ),
              TextField(
                controller: passwordController,
                decoration: InputDecoration(hintText: "Password"),
              ),
              ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder:
                          (context) => displayPage(
                            email: emailController.text,
                            password: passwordController.text,
                          ),
                    ),
                  );
                  print(emailController.text);
                  print(passwordController.text);
                },
                child: Text("submit"),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class displayPage extends StatefulWidget {
  final String email, password;
  const displayPage({Key? key, required this.email, required this.password})
    : super(key: key);

  @override
  State<displayPage> createState() => _displayPageState();
}

class _displayPageState extends State<displayPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("displayPage")),
      body: Center(
        child: Text("Email: ${widget.email} Password: ${widget.password}"),
      ),
    );
  }
}

class DemoApp extends StatelessWidget {
  const DemoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.blue,
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.center,
        children: const <Widget>[
          Text("Hello world!", textDirection: TextDirection.ltr),
          Text("Hello world!", textDirection: TextDirection.ltr),
        ],
      ),
    );
  }
}

class DemoApp2 extends StatefulWidget {
  const DemoApp2({super.key});

  @override
  State<DemoApp2> createState() => _DemoApp2State();
}

class _DemoApp2State extends State<DemoApp2> {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text("Hello")),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              TextButton(onPressed: onPressed, child: Text("Button")),
              Text("$count"),
            ],
          ),
        ),
      ),
    );
  }

  int count = 0;
  void onPressed() {
    setState(() {
      count++;
    });
  }
}
