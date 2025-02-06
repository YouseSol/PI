import 'dart:developer';

import 'package:flutter/material.dart';

import 'package:pi/API/client.dart';
import 'package:pi/API/lead_api_extension.dart';

import 'package:pi/form/lead_form.dart';

import 'package:pi/domain/lead.dart';


class LeadsPage extends StatefulWidget {
  final PIClient apiClient;

  const LeadsPage({ super.key, required this.apiClient });

  @override
  State<LeadsPage> createState() => _LeadsPageState();
}

class _LeadsPageState extends State<LeadsPage> {
  final chatScrollController = ScrollController();

  int pageSize = 10;
  int _page = 0;

  int get page => _page;

  set page(int value) {
    _page = value < 0 ? 0 : value;
  }

  List<DataRow> widgets = List.empty(growable: true);

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollToEnd();
    });
  }

  void _scrollToEnd() {
    if (chatScrollController.hasClients) {
      chatScrollController.jumpTo(chatScrollController.position.maxScrollExtent);
    }
  }

  @override
  Widget build(BuildContext context) {
    // const searchBar = SearchBar(
    //   shape: WidgetStatePropertyAll<OutlinedBorder>(RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(4.0))))
    // );

    final pageSizeDropdown = Padding(
      padding: const EdgeInsets.all(2.0),
      child: DropdownMenu<int>(
        initialSelection: 10,
        dropdownMenuEntries: const [
          DropdownMenuEntry(value: 10, label: '10'),
          DropdownMenuEntry(value: 25, label: '25'),
          DropdownMenuEntry(value: 50, label: '50'),
          DropdownMenuEntry(value: 100, label: '100'),
        ],
        onSelected: (value) {
          if (value == null) return;

          setState(() => pageSize = value);
        }
      )
    );

    return Expanded(child: Column(children: [
      Padding(padding: const EdgeInsets.only(right: 15.0, left: 15.0, top: 5.0, bottom: 5.0), child: Row(children: [
        pageSizeDropdown,
        const Spacer(flex: 150),
        IconButton(icon: const Icon(Icons.arrow_left), onPressed: () => setState(() => page = page - 1)),
        const Spacer(flex: 1),
        Text((page + 1).toString()),
        const Spacer(flex: 1),
        IconButton(icon: const Icon(Icons.arrow_right), onPressed: () => setState(() => page = page + 1)),
        // Spacer(flex: 1),
        // Expanded(flex: 98, child: searchBar),
        // Spacer(flex: 1),
      ])),
      buildList()
    ]));
  }

  Widget buildList() {
    late List<DataRow> rows;

    return Expanded(child: FutureBuilder<List<Lead>>(
      future: widget.apiClient.fetchLeads(pageSize, page),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          rows = [];
        } else {
          final leads = snapshot.data!;
          rows= leads.map(buildDataRow).toList();
        }

        return SingleChildScrollView(child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            DataTable(
              columns: const [
                DataColumn(label: SizedBox(width: 200, child: Text("Primeiro Nome"))),
                DataColumn(label: SizedBox(width: 200, child: Text("Ultimo Nome"))),
                DataColumn(label: SizedBox(width: 200, child: Text("Status"))),
                DataColumn(label: SizedBox(width: 50, child: Text("Ações")))
              ],
              rows: rows,
            ),
            if (snapshot.connectionState == ConnectionState.waiting) const Center(child: CircularProgressIndicator())
          ]
        ));
      }
    ));
  }

  DataRow buildDataRow(Lead l) {
    return DataRow(
      cells: [
        DataCell(SelectableText(l.firstName)),
        DataCell(SelectableText(l.lastName)),
        DataCell(SelectableText(l.active ? "Ativo" : "Inativo")),
        DataCell(Row(children: [
          IconButton(
            icon: const Icon(Icons.create),
            onPressed: () {
              showDialog(
                barrierDismissible: false,
                context: context,
                builder: (BuildContext context) {
                  return AlertDialog(
                    title: const Text("Editar Lead"),
                    content: LeadForm(apiClient: widget.apiClient, lead: l),
                  );
                }
              ).then((value) => setState(() => ()));
            },
          ),
          const Spacer(flex:  1),
          IconButton(
            icon: const Icon(Icons.delete),
            onPressed: () {
              showDialog(
                barrierDismissible: false,
                context: context,
                builder: (context) => DeleteLeadDialog(onDelete: () => widget.apiClient.deleteLead(l))
              ).then((value) {
                if (value as bool) {
                  setState(() => ());
                }
              });
            },
          ),
          const Spacer(flex: 150)
        ]))
      ],
    );
  }
}

class DeleteLeadDialog extends StatefulWidget {
  final Future<void> Function() onDelete;

  const DeleteLeadDialog({ super.key, required this.onDelete });

  @override
  State<DeleteLeadDialog> createState() => _DeleteLeadDialogState();
}

class _DeleteLeadDialogState extends State<DeleteLeadDialog> {
  bool isLoading = false;

  void _handleDelete() async {
    setState(() => isLoading = true);

    await widget.onDelete();

    if (context.mounted) {
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      icon: const Icon(Icons.info),
      iconColor: Colors.black,
      title: Text(!isLoading ? "Deseja mesmo deletar este lead?" : "Deletando"),
      content: isLoading ? const Center(heightFactor: 0.5, child: CircularProgressIndicator())
                         : const Text("Esta ação não pode ser desfeita."),
      actions: [
        if (!isLoading)
          TextButton(
            onPressed: _handleDelete,
            child: const Text("Confirmar"),
          ),
        if (!isLoading) TextButton(onPressed: () => Navigator.of(context).pop(false), child: const Text("Cancelar")),
      ],
    );
  }
}
