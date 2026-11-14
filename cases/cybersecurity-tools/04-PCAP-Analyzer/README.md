# PCAP Analyzer

Учебный офлайн-анализ TCP-трафика: много целевых портов с одного IP и большое число SYN без ACK. Использует только стандартную библиотеку Python.

```powershell
python pcap_analyzer.py sample.pcap --port-threshold 3 --syn-threshold 4 --json findings.json
python -m unittest discover -v
```

В комплекте есть искусственный `sample.pcap` для проверки команды. Поддерживается **только классический PCAP с Ethernet (linktype 1), без VLAN, IPv6 extension headers и PCAPNG**. Для реального трафика результат ограничен этими условиями. Используйте только разрешённые захваты; эвристики дают ложные срабатывания и пропуски.
