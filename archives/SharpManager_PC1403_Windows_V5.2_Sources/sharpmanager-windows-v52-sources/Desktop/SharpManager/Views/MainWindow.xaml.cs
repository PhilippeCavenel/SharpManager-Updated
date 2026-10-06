using System;
using System.Collections.Generic;
using System.Data.Common;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

using Microsoft.Win32;

using SharpManager.ViewModels;

using static System.Net.Mime.MediaTypeNames;

namespace SharpManager.Views
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window, IMessageTarget
    {
        /// <summary>
        /// The view model
        /// </summary>
        private readonly MainViewModel viewModel;

        /// <summary>
        /// Initializes a new instance of the <see cref="MainWindow"/> class.
        /// </summary>
        public MainWindow()
        {
            InitializeComponent();

            System.Windows.Application.Current.DispatcherUnhandledException += Application_DispatcherUnhandledException;
            TaskScheduler.UnobservedTaskException += TaskScheduler_UnobservedTaskException;

            viewModel = new MainViewModel(this);
            DataContext = viewModel;

            // Apppend newline after version text
            Log.AppendText(" " + App.Version.ToString(3) + "\r\n");
            Log.ScrollToEnd();
        }

        /// <summary>
        /// Tasks the scheduler unobserved task exception.
        /// </summary>
        /// <param name="sender">The sender.</param>
        /// <param name="e">The <see cref="UnobservedTaskExceptionEventArgs"/> instance containing the event data.</param>
        private void TaskScheduler_UnobservedTaskException(object? sender, UnobservedTaskExceptionEventArgs e)
        {
            e.SetObserved();
            if (e.Exception.Flatten().InnerExceptions.All(ex => ex is TaskCanceledException)) return;
            Dispatcher.InvokeAsync(() =>
            {
                foreach (var exception in e.Exception.Flatten().InnerExceptions)
                {
                    if (exception is TaskCanceledException) continue;
                    MessageBox.Show(this, e.Exception.Message, "An error occurred", MessageBoxButton.OK, MessageBoxImage.Error);
                    if (viewModel.ShowDebug) ((IMessageTarget)this).WriteLine(exception.ToString());
                }
            });
        }

        /// <summary>
        /// Handles the DispatcherUnhandledException event of the Application control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="System.Windows.Threading.DispatcherUnhandledExceptionEventArgs"/> instance containing the event data.</param>
        private void Application_DispatcherUnhandledException(object sender, System.Windows.Threading.DispatcherUnhandledExceptionEventArgs e)
        {
            e.Handled = true;
            if (e.Exception is TaskCanceledException) return;
            Dispatcher.InvokeAsync(() =>
            {
                MessageBox.Show(this, e.Exception.Message, "An error occurred", MessageBoxButton.OK, MessageBoxImage.Error);
                if (viewModel.ShowDebug) ((IMessageTarget)this).WriteLine(e.Exception.ToString());
            });
        }

        /// <summary>
        /// Handles the Click event of the OpenFile control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void SendBasic_Click(object sender, RoutedEventArgs e)
        {
            if (!viewModel.CanStartTransfer) return;
            var dialog = new OpenFileDialog
            {
                Title = "Envoyer un programme BASIC au PC-1403",
                Filter = "Programmes BASIC (*.bas)|*.bas|Fichiers texte (*.txt)|*.txt"
            };
            if (dialog.ShowDialog(this) != true) return;

            viewModel.IsConvertingBasic = true;
            ConnectionToolbar.IsEnabled = false;
            try
            {
                Log.AppendText($"Préparation BASIC PC-1403 : {dialog.FileName}\r\n");
                byte[] tape = await BasicTapeConverter.ConvertAsync(dialog.FileName,
                    System.IO.Path.Combine(AppContext.BaseDirectory, "PocketTools"),
                    text => Dispatcher.Invoke(() => Log.AppendText(text + "\r\n")));
                ConnectionToolbar.IsEnabled = true;
                // Conversion is finished before asking the user to start reception;
                // the Sharp therefore never waits while the converter is still running.
                if (MessageBox.Show(this,
                    "Sur le Sharp PC-1403, passez en RUN, saisissez CLOAD puis ENTER.\n\n" +
                    "Cliquez ensuite sur OK pour envoyer le programme.\n" +
                    "Le chargement remplacera le programme présent sur le Sharp.",
                    "Sharp prêt à recevoir ?", MessageBoxButton.OKCancel,
                    MessageBoxImage.Information) != MessageBoxResult.OK) return;
                if (!viewModel.IsConnected) throw new IOException("La liaison série a été déconnectée.");
                using var stream = new MemoryStream(tape, writable: false);
                await viewModel.Arduino.SendTapeFile(stream);
                Log.AppendText("Signal cassette terminé. Vérifiez CLOAD sur le Sharp, puis saisissez RUN.\r\n");
            }
            catch (OperationCanceledException)
            {
                Log.AppendText("Envoi BASIC annulé.\r\n");
            }
            catch (Exception exception)
            {
                Log.AppendText("Erreur BASIC : " + exception.Message + "\r\n");
                MessageBox.Show(this, exception.Message, "Envoi BASIC", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                viewModel.IsConvertingBasic = false;
                ConnectionToolbar.IsEnabled = true;
                Log.ScrollToEnd();
            }
        }

        private async void OpenFile_Click(object sender, RoutedEventArgs e)
        {
            if (!viewModel.CanStartTransfer) return;
            var openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Tape files (*.tap)|*.tap|All files (*.*)|*.*";
            if (openFileDialog.ShowDialog() == true)
            {
                viewModel.IsConvertingBasic = true;
                try
                {
                    Log.AppendText($"Envoi TAP : {openFileDialog.FileName}\r\n");
                    using var fileStream = new FileStream(openFileDialog.FileName, FileMode.Open, FileAccess.Read);
                    await viewModel.Arduino.SendTapeFile(fileStream);
                    Log.AppendText("Envoi terminé ; vérifiez CLOAD sur le Sharp.\r\n");
                }
                catch (Exception exception)
                {
                    Log.AppendText("Erreur TAP : " + exception.Message + "\r\n");
                    MessageBox.Show(this, exception.Message, "Envoi TAP", MessageBoxButton.OK, MessageBoxImage.Error);
                }
                finally { viewModel.IsConvertingBasic = false; Log.ScrollToEnd(); }
            }
        }

        /// <summary>
        /// Handles the Click event of the OpenFile control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void ReceiveFile_Click(object sender, RoutedEventArgs e)
        {
            byte[] data;
            try { data = await viewModel.Arduino.ReadTapeFile(); }
            catch (OperationCanceledException) { Log.AppendText("Réception annulée.\r\n"); return; }
            catch (Exception exception) { ((IMessageTarget)this).ShowException(exception); return; }

            var dialog = new SaveFileDialog
            {
                Title = "Enregistrer le programme reçu par CSAVE",
                Filter = "Programme BASIC (*.bas)|*.bas|Cassette Sharp (*.tap)|*.tap",
                FileName = "PROGRAMME",
                DefaultExt = ".bas",
                AddExtension = true
            };
            if (dialog.ShowDialog(this) != true) return;
            bool asBasic = string.Equals(System.IO.Path.GetExtension(dialog.FileName), ".bas", StringComparison.OrdinalIgnoreCase)
                || (!string.Equals(System.IO.Path.GetExtension(dialog.FileName), ".tap", StringComparison.OrdinalIgnoreCase) && dialog.FilterIndex == 1);
            if (!asBasic)
            {
                await File.WriteAllBytesAsync(dialog.FileName, data);
                Log.AppendText($"Cassette sauvegardée : {dialog.FileName}\r\n");
                return;
            }
            viewModel.IsConvertingBasic = true;
            ConnectionToolbar.IsEnabled = false;
            try
            {
                // Decode completely before opening the destination. A failed conversion
                // must neither erase an existing BASIC file nor discard received bytes.
                string source = await BasicTapeConverter.DecodeAsync(data,
                    System.IO.Path.Combine(AppContext.BaseDirectory, "PocketTools"),
                    text => Dispatcher.Invoke(() => Log.AppendText(text + "\r\n")));
                await File.WriteAllTextAsync(dialog.FileName, source, new UTF8Encoding(false));
                Log.AppendText($"Programme BASIC sauvegardé : {dialog.FileName}\r\n");
            }
            catch (Exception exception)
            {
                Log.AppendText("Export BASIC impossible : " + exception.Message + "\r\n");
                MessageBox.Show(this, exception.Message + "\n\nLes données reçues sont conservées pour les enregistrer en .tap.",
                    "Export CSAVE", MessageBoxButton.OK, MessageBoxImage.Information);
                var fallback = new SaveFileDialog
                {
                    Title = "Sauvegarder la cassette reçue",
                    Filter = "Cassette Sharp (*.tap)|*.tap",
                    FileName = System.IO.Path.GetFileNameWithoutExtension(dialog.FileName),
                    InitialDirectory = System.IO.Path.GetDirectoryName(dialog.FileName),
                    DefaultExt = ".tap"
                };
                if (fallback.ShowDialog(this) == true)
                    await File.WriteAllBytesAsync(fallback.FileName, data);
            }
            finally
            {
                viewModel.IsConvertingBasic = false;
                ConnectionToolbar.IsEnabled = true;
                Log.ScrollToEnd();
            }
        }

        /// <summary>
        /// Handles the Click event of the SelectDiskFolder control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void SelectDiskFolder_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new OpenFolderDialog
            {
                Title = "Select Disk Folder",
                InitialDirectory = viewModel.DiskDirectory
            };

            if (dialog.ShowDialog() == true)
            {
                viewModel.DiskDirectory = dialog.FolderName;
            }
        }

        /// <summary>
        /// Handles the Click event of the Clear control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void Clear_Click(object sender, RoutedEventArgs e)
        {
            Log.Clear();
        }

        /// <summary>
        /// Handles the Click event of the Exit control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void Exit_Click(object sender, RoutedEventArgs e)
        {
            System.Windows.Application.Current.Shutdown();
        }

        /// <summary>
        /// Handles the Click event of the Connect control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private async void Connect_Click(object sender, RoutedEventArgs e)
        {
            await viewModel.Connect();
        }

        /// <summary>
        /// Handles the Click event of the Disconnect control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void Disconnect_Click(object sender, RoutedEventArgs e)
        {
            viewModel.Disconnect();
        }

        private async void Ping_Click(object sender, RoutedEventArgs e)
        {
            await viewModel.Arduino.Ping();
        }

        /// <summary>
        /// Handles the Click event of the Cancel control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void Cancel_Click(object sender, RoutedEventArgs e)
        {
            viewModel.Cancel();
        }

        /// <summary>
        /// Handles the PreviewKeyDown event of the Window control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="KeyEventArgs"/> instance containing the event data.</param>
        private void Window_PreviewKeyDown(object sender, KeyEventArgs e)
        {
            if (e.Key == Key.Escape && viewModel.CanCancel)
            {
                viewModel.Cancel();
                e.Handled = true;   
            }
        }

        /// <summary>
        /// Write the specified message.
        /// </summary>
        /// <param name="message">The message.</param>
        void IMessageTarget.Write(string message)
        {
            Dispatcher.InvokeAsync(() => {
                Log.AppendText(message);
                Log.ScrollToEnd();
            });
        }

        /// <summary>
        /// Shows the specified exception
        /// </summary>
        /// <param name="exception">The exception.</param>
        void IMessageTarget.ShowException(Exception exception)
        {
            if (exception is TaskCanceledException) return;
            Dispatcher.InvokeAsync(() =>
            {
                MessageBox.Show(this, exception.Message, "An error occurred", MessageBoxButton.OK, MessageBoxImage.Error);
                if (viewModel.ShowDebug) ((IMessageTarget)this).WriteLine(exception.ToString());
            });
        }

        /// <summary>
        /// Handles the Click event of the About control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void About_Click(object sender, RoutedEventArgs e)
        {
            var about = new About();
            about.Owner = this;
            about.ShowDialog();
        }

        /// <summary>
        /// Handles the Click event of the UploadFirmware control.
        /// </summary>
        /// <param name="sender">The source of the event.</param>
        /// <param name="e">The <see cref="RoutedEventArgs"/> instance containing the event data.</param>
        private void UploadFirmware_Click(object sender, RoutedEventArgs e)
        {
            UploadFirmware.ShowDialog(this, viewModel);
        }


    }
}
 
