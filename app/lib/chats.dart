import 'dart:developer';

import 'package:flutter/material.dart';

import 'package:intl/intl.dart';

import 'package:pi/PIAPI/client.dart';
import 'package:pi/PIAPI/lead_api_extension.dart';

import 'package:pi/PIAPI/domain/lead.dart';


class LeadSelectionNotifier with ChangeNotifier {
  Lead? _lead;
  Lead? get lead => _lead;

  void setLead(Lead? value) {
    _lead = value;
    notifyListeners();
  }
}

class ChatsPage extends StatefulWidget {
  final PIClient apiClient;

  const ChatsPage({ super.key, required this.apiClient });

  @override
  State<ChatsPage> createState() => _ChatsPageState();
}

class _ChatsPageState extends State<ChatsPage> {
  final leadSelectionNotifier = LeadSelectionNotifier();

  @override
  Widget build(BuildContext context) {
    return  Expanded(child: Row(children: [
      Expanded(flex: 2, child: Center(child: AvailableChats(apiClient: widget.apiClient, onLeadSelected: leadSelectionNotifier.setLead))),
      Expanded(flex: 10, child: Center(child: ChatHistory(apiClient: widget.apiClient, leadSelectionNotifier: leadSelectionNotifier))),
    ]));
  }
}

class AvailableChats extends StatefulWidget {
  final PIClient apiClient;
  final void Function(Lead) onLeadSelected;

  const AvailableChats({ super.key, required this.apiClient, required this.onLeadSelected });

  @override
  State<AvailableChats> createState() => _AvailableChats();
}

class _AvailableChats extends State<AvailableChats> {
  List<Lead> leads = List.empty(growable: true);

  Lead? selectedLead;

  bool hasTriedLoading = false;
  bool isLoading = false;

  int pageSize = 50;
  int page = 0;

  @override
  Widget build(BuildContext context) {
    return NotificationListener<ScrollNotification>(
      child: buildListView(),
      onNotification: (n) {
        if (n is ScrollEndNotification) {
          loadMore();
        }
        return true;
      }
    );
  }

  void loadMore() {
    if (isLoading) {
      return;
    }

    isLoading = true;

    widget.apiClient.fetchLeads(pageSize, page).then((leads_) async {
      leads.addAll(leads_);

      await Future.delayed(const Duration(seconds: 2));

      if (!mounted) {
        return;
      }

      setState(() {
        if (leads_.length >= pageSize) {
          page = page + 1;
        }
        hasTriedLoading = true;
        isLoading = false;
      });
    });
  }

  Widget buildListView() {
    if (!hasTriedLoading) {
      loadMore();
    }

    return ListView(children: leads.map(buildLeadTile).toList());
  }

  Widget buildLeadTile(Lead l) {
    return ListTile(
      leading: const Icon(Icons.account_circle),
      title: Text('${l.firstName} ${l.lastName}', overflow: TextOverflow.ellipsis),
      selected: (selectedLead?.id ?? 0) == l.id,
      selectedColor: Colors.black,
      selectedTileColor: Colors.grey,
      onTap: () {
        setState(() => selectedLead = l);
        widget.onLeadSelected(l);
      }
    );
  }
}

class ChatHistory extends StatefulWidget {
  final PIClient apiClient;
  final LeadSelectionNotifier leadSelectionNotifier;

  const ChatHistory({ super.key, required this.apiClient, required this.leadSelectionNotifier });

  @override
  State<ChatHistory> createState() => _ChatHistory();
}

class _ChatHistory extends State<ChatHistory> {

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: widget.leadSelectionNotifier,
      builder: (BuildContext context, Widget? child) {

      if (widget.leadSelectionNotifier.lead == null) {
        return const Text("Por favor, selecione uma conversa.");
      }

      return FutureBuilder<List<Map>>(
        future: widget.apiClient.fetchChatHistory(widget.leadSelectionNotifier.lead!),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Column(children: [
              Spacer(flex: 99),
              CircularProgressIndicator(),
              Spacer(flex: 2),
              Text("Buscando mensagens."),
              Spacer(flex: 99),
            ]);
          } else {
            final chatHistory = snapshot.data!;

            if (chatHistory.isEmpty) {
              return const Center(child: Text("Nada para mostrar aqui."));
            }

            return buildChat_(chatHistory);
          }
        }
      );
      }
    );
  }

  Widget buildChat_(List<Map> messages) {
    return ListView.builder(
      itemCount: messages.length,
      itemBuilder: (context, idx) {
        final e = messages[idx];

        final color = e["role"] == "agent" ? Colors.white70 : const Color.fromRGBO(217, 253, 211, 1.0);
        final mainAxisAlignment = e["role"] == "agent" ? MainAxisAlignment.end : MainAxisAlignment.start;
        final alignment = e["role"] == "agent" ? Alignment.centerRight : Alignment.centerLeft;
        final date = DateTime.fromMillisecondsSinceEpoch((e["timestamp"] as int) * 1000);

        final formatter = DateFormat("dd/MM/yyyy HH:mm");

        return FractionallySizedBox(
          widthFactor: 0.45,
          alignment: alignment,
          child: Container(
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(10),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  spreadRadius: 1,
                  blurRadius: 5,
                  offset: const Offset(2, 2),
                ),
              ],
            ),
            padding: const EdgeInsets.all(10),
            margin: const EdgeInsets.only(top: 5, left: 15.0, right: 15.0, bottom: 15),
            child: Column(
              children: [
                Row(mainAxisAlignment: mainAxisAlignment, children: [
                  Expanded(flex: 5, child: Text(e["content"], style: const TextStyle(fontSize: 16))),
                ]),
                const SizedBox(height: 5),
                Row(mainAxisAlignment: mainAxisAlignment, children: [
                  Text(formatter.format(date), style: const TextStyle(fontSize: 12, color: Colors.grey)),
                ]),
                const SizedBox(height: 5),
            ]),
          )
        );
      }
    );
  }
}
