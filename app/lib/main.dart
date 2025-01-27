import 'dart:developer';

import 'package:flutter/material.dart';

import 'package:pi/campaigns.dart';
import 'package:pi/chats.dart';

import 'package:pi/PIAPI/client.dart';
import 'package:pi/leads.dart';


void main() {
  runApp(const PIApp());
}

class PIApp extends StatelessWidget {
  const PIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PI',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blueAccent),
        useMaterial3: true,
        textButtonTheme: const TextButtonThemeData(
          style: ButtonStyle(
            foregroundColor: WidgetStatePropertyAll<Color>(Colors.white),
            backgroundColor: WidgetStatePropertyAll<Color>(Colors.blue),
            shape: WidgetStatePropertyAll<OutlinedBorder>(RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(4.0))))
          )
        ),
        iconButtonTheme: const IconButtonThemeData(
          style: ButtonStyle(
            foregroundColor: WidgetStatePropertyAll<Color>(Colors.white),
            backgroundColor: WidgetStatePropertyAll<Color>(Colors.lightBlue),
            shape: WidgetStatePropertyAll<OutlinedBorder>(RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(4.0))))
          )
        ),
        dialogTheme: const DialogTheme(
          iconColor: Colors.black,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(2.0)))
        ),
        scrollbarTheme: const ScrollbarThemeData(
          trackVisibility: WidgetStatePropertyAll<bool>(true),
          thumbVisibility: WidgetStatePropertyAll<bool>(true)
        )
      ),
      home: const HomePage(title: 'PI - Início'),
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key, required this.title});

  final String title;

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  String selectedSidebarItem = 'Home';

  PIClient apiClient = PIClient();

  final emailController = TextEditingController();
  final passwordController = TextEditingController();

  void onSidebarItemSelected(String item) {
    setState(() => selectedSidebarItem = item);
  }

  void login() {
    apiClient.login(email: emailController.text, password: passwordController.text)
             .then(
               (_) => setState(() {
                 emailController.clear();
                 passwordController.clear();
               }),
               onError: (_) {
                 emailController.clear();
                 passwordController.clear();

                 if (!context.mounted) {
                   return;
                 }

                 showDialog(context: context, builder: (context) {
                   return const AlertDialog(
                     icon: Icon(Icons.info),
                     title: Text("Falha ao autenticar."),
                     content: Text("Login e/ou senha inválido(s)."),
                   );
                 });
               }
             );
  }

  void logout() {
    showDialog(context: context, builder: (context) {
      return AlertDialog(
        icon: const Icon(Icons.info),
        title: const Text("Deseja mesmo sair?"),
        actions: [
          TextButton(onPressed: logoutImpl, child: const Text("Confirmar")),
          TextButton(onPressed: () {
            Navigator.of(context).pop();
          }, child: const Text("Cancelar"))
        ],
      );
    });
  }

  void logoutImpl() {
    emailController.clear();
    passwordController.clear();

    apiClient.logout();

    if (context.mounted) {
      Navigator.of(context).pop();
    }

    setState(() => ());
  }

  @override
  Widget build(BuildContext context) {
    final emailField = TextFormField(
      keyboardType: TextInputType.emailAddress,
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        label: Text("Email"),
        floatingLabelBehavior: FloatingLabelBehavior.always,
      ),
      controller: emailController
    );

    final passwordField = TextFormField(
      decoration: const InputDecoration(
        border: OutlineInputBorder(),
        label: Text("Senha"),
        floatingLabelBehavior: FloatingLabelBehavior.always,
      ),
      controller: passwordController,
      obscureText: true
    );

    final confirmButton = TextButton(onPressed: login, child: const Text("Confirmar"));

    const divider = Divider(height: 8, color: Colors.transparent);

    late Widget widget;

    if (!apiClient.isAuthenticated()) {
      widget = Padding(padding: const EdgeInsets.all(20),child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        emailField,
        divider,
        passwordField,
        divider,
        confirmButton
      ]));
    } else {
      widget = Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
        SizedBox(
          width: 200,
          child: Drawer(
            shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
            child: ListView(
              padding: EdgeInsets.zero,

              children: [
                ListTile(
                  title: const Text('Início'),
                  leading: const Icon(Icons.home),
                  onTap: () => onSidebarItemSelected('Home'),
                  selected: selectedSidebarItem == 'Home',
                  selectedTileColor: Colors.blue[100],
                  selectedColor: Colors.white
                ),
                ListTile(
                  title: const Text('Campanhas'),
                  leading: const Icon(Icons.file_upload),
                  onTap: () => onSidebarItemSelected('Campaigns'),
                  selected: selectedSidebarItem == 'Campaigns',
                  selectedTileColor: Colors.blue[100],
                  selectedColor: Colors.white
                ),
                ListTile(
                  title: const Text('Conversas'),
                  leading: const Icon(Icons.chat),
                  onTap: () => onSidebarItemSelected('Chats'),
                  selected: selectedSidebarItem == 'Chats',
                  selectedTileColor: Colors.blue[100],
                  selectedColor: Colors.white
                ),
                ListTile(
                  title: const Text('Leads'),
                  leading: const Icon(Icons.person),
                  onTap: () => onSidebarItemSelected('Leads'),
                  selected: selectedSidebarItem == 'Leads',
                  selectedTileColor: Colors.blue[100],
                  selectedColor: Colors.white
                ),
                ListTile(
                  title: const Text('Sair'),
                  leading: const Icon(Icons.logout),
                  onTap: logout,
                ),
              ],
            )),
        ),
        buildMainContent()
      ]);
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('[P]rospectador [I]nteligente'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white
      ),
      body: widget
    );
  }

  Widget buildMainContent() {
    switch (selectedSidebarItem) {
      case "Home":
        return Expanded(child: Center(child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextButton(
              onPressed: flipAccountStatus,
              child: Text("${apiClient.user!.active ? 'Desativar': 'Ativar'} conta")
            )
          ],
        )));

      case "Chats":
        return ChatsPage(apiClient: apiClient);

      case "Campaigns":
        return CampaignsPage(apiClient: apiClient);

      case "Leads":
        return LeadsPage(apiClient: apiClient);

      default:
        return const Expanded(child: Center(child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [ Text('Error') ],
        )));
    }
  }

  void flipAccountStatus() {

  }
}
