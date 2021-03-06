#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the event formatters manager."""

from __future__ import unicode_literals

import unittest

from plaso.formatters import manager
from plaso.formatters import mediator
from plaso.formatters import winreg  # pylint: disable=unused-import
from plaso.lib import definitions

from tests import test_lib as shared_test_lib
from tests.containers import test_lib as containers_test_lib
from tests.formatters import test_lib


class FormattersManagerTest(shared_test_lib.BaseTestCase):
  """Tests for the event formatters manager."""

  # pylint: disable=protected-access

  _TEST_EVENTS = [
      {'data_type': 'test:event',
       'filename': 'c:/Users/joesmith/NTUSER.DAT',
       'hostname': 'MYHOSTNAME',
       'random': 'random',
       'text': '',
       'timestamp': 0,
       'timestamp_desc': definitions.TIME_DESCRIPTION_UNKNOWN,
       'username': 'joesmith'},
      {'data_type': 'windows:registry:key_value',
       'hostname': 'MYHOSTNAME',
       'key_path': 'MY AutoRun key',
       'timestamp': '2012-04-20 22:38:46.929596',
       'timestamp_desc': definitions.TIME_DESCRIPTION_WRITTEN,
       'values': 'Value: c:/Temp/evil.exe'},
      {'data_type': 'windows:registry:key_value',
       'hostname': 'MYHOSTNAME',
       'key_path': 'HKEY_CURRENT_USER\\Secret\\EvilEmpire\\Malicious_key',
       'timestamp': '2012-04-20 23:56:46.929596',
       'timestamp_desc': definitions.TIME_DESCRIPTION_WRITTEN,
       'values': 'Value: send all the exes to the other world'},
      {'data_type': 'windows:registry:key_value',
       'hostname': 'MYHOSTNAME',
       'key_path': 'HKEY_CURRENT_USER\\Windows\\Normal',
       'timestamp': '2012-04-20 16:44:46',
       'timestamp_desc': definitions.TIME_DESCRIPTION_WRITTEN,
       'values': 'Value: run all the benign stuff'},
      {'data_type': 'test:event',
       'filename': 'c:/Temp/evil.exe',
       'hostname': 'MYHOSTNAME',
       'text': 'This log line reads ohh so much.',
       'timestamp': '2012-04-30 10:29:47.929596',
       'timestamp_desc': definitions.TIME_DESCRIPTION_UNKNOWN},
      {'data_type': 'test:event',
       'filename': 'c:/Temp/evil.exe',
       'hostname': 'MYHOSTNAME',
       'text': 'Nothing of interest here, move on.',
       'timestamp': '2012-04-30 10:29:47.929596',
       'timestamp_desc': definitions.TIME_DESCRIPTION_UNKNOWN},
      {'data_type': 'test:event',
       'filename': 'c:/Temp/evil.exe',
       'hostname': 'MYHOSTNAME',
       'text': 'Mr. Evil just logged into the machine and got root.',
       'timestamp': '2012-04-30 13:06:47.939596',
       'timestamp_desc': definitions.TIME_DESCRIPTION_UNKNOWN},
      {'data_type': 'test:event',
       'filename': 'c:/Temp/evil.exe',
       'hostname': 'nomachine',
       'offset': 12,
       'text': (
           'This is a line by someone not reading the log line properly. And '
           'since this log line exceeds the accepted 80 chars it will be '
           'shortened.'),
       'timestamp': '2012-06-05 22:14:19.000000',
       'timestamp_desc': definitions.TIME_DESCRIPTION_WRITTEN,
       'username': 'johndoe'}]

  def testReadFormattersFile(self):
    """Tests the _ReadFormattersFile function."""
    test_file_path = self._GetTestFilePath(['formatters', 'format_test.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    manager.FormattersManager.Reset()
    number_of_formatters = len(manager.FormattersManager._formatter_classes)

    manager.FormattersManager._ReadFormattersFile(test_file_path)
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters + 1)

    manager.FormattersManager.Reset()
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters)

  def testReadFormattersFromDirectory(self):
    """Tests the ReadFormattersFromDirectory function."""
    test_directory_path = self._GetTestFilePath(['formatters'])
    self._SkipIfPathNotExists(test_directory_path)

    manager.FormattersManager.Reset()
    number_of_formatters = len(manager.FormattersManager._formatter_classes)

    manager.FormattersManager.ReadFormattersFromDirectory(test_directory_path)
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters + 1)

    manager.FormattersManager.Reset()
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters)

  def testReadFormattersFromFile(self):
    """Tests the ReadFormattersFromFile function."""
    test_file_path = self._GetTestFilePath(['formatters', 'format_test.yaml'])
    self._SkipIfPathNotExists(test_file_path)

    manager.FormattersManager.Reset()
    number_of_formatters = len(manager.FormattersManager._formatter_classes)

    manager.FormattersManager.ReadFormattersFromFile(test_file_path)
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters + 1)

    manager.FormattersManager.Reset()
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters)

  def testFormatterRegistration(self):
    """Tests the RegisterFormatter and DeregisterFormatter functions."""
    number_of_formatters = len(manager.FormattersManager._formatter_classes)

    manager.FormattersManager.RegisterFormatter(test_lib.TestEventFormatter)
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters + 1)

    with self.assertRaises(KeyError):
      manager.FormattersManager.RegisterFormatter(test_lib.TestEventFormatter)

    manager.FormattersManager.DeregisterFormatter(test_lib.TestEventFormatter)
    self.assertEqual(
        len(manager.FormattersManager._formatter_classes),
        number_of_formatters)

  def testMessageStrings(self):
    """Tests the GetMessageStrings function."""
    formatter_mediator = mediator.FormatterMediator(
        data_location=shared_test_lib.TEST_DATA_PATH)

    message_strings = []
    text_message = None
    text_message_short = None

    manager.FormattersManager.RegisterFormatter(test_lib.TestEventFormatter)

    try:
      for event, event_data, _ in containers_test_lib.CreateEventsFromValues(
          self._TEST_EVENTS):
        message, message_short = manager.FormattersManager.GetMessageStrings(
            formatter_mediator, event_data)

        text_message = message
        text_message_short = message_short

        csv_message_strings = '{0:d},{1:s}'.format(event.timestamp, message)
        message_strings.append(csv_message_strings)

    finally:
      manager.FormattersManager.DeregisterFormatter(test_lib.TestEventFormatter)

    self.assertIn(
        '1334961526929596,[MY AutoRun key] Value: c:/Temp/evil.exe',
        message_strings)

    self.assertIn(
        ('1334966206929596,[HKEY_CURRENT_USER\\Secret\\EvilEmpire\\'
         'Malicious_key] Value: send all the exes to the other world'),
        message_strings)
    self.assertIn((
        '1334940286000000,[HKEY_CURRENT_USER\\Windows\\Normal] '
        'Value: run all the benign stuff'), message_strings)
    self.assertIn(
        '1335781787929596,This log line reads ohh so much.',
        message_strings)
    self.assertIn(
        '1335781787929596,Nothing of interest here, move on.',
        message_strings)
    self.assertIn(
        '1335791207939596,Mr. Evil just logged into the machine and got root.',
        message_strings)

    expected_text_message = (
        'This is a line by someone not reading the log line properly. And '
        'since this log line exceeds the accepted 80 chars it will be '
        'shortened.')
    self.assertEqual(text_message, expected_text_message)

    expected_text_message_short = (
        'This is a line by someone not reading the log line properly. '
        'And since this l...')
    self.assertEqual(text_message_short, expected_text_message_short)

  def testGetUnformattedAttributes(self):
    """Tests the GetUnformattedAttributes function."""
    _, event_data, _ = containers_test_lib.CreateEventFromValues(
        self._TEST_EVENTS[0])

    manager.FormattersManager.RegisterFormatter(test_lib.TestEventFormatter)

    try:
      unformatted_attributes = (
          manager.FormattersManager.GetUnformattedAttributes(event_data))
    finally:
      manager.FormattersManager.DeregisterFormatter(test_lib.TestEventFormatter)

    self.assertEqual(
        unformatted_attributes, ['_event_data_stream_row_identifier', 'random'])


if __name__ == '__main__':
  unittest.main()
