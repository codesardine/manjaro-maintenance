#!/usr/bin/env python3

import gi, subprocess, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

branch = (
            "Stable",
            "Testing",
            "Unstable"
        )

issues = (
            "Reinstall All Packages",
            "Reinstall Keyrings",
            "Rebuild Initramfs"
        )

def rebuild_kernel():
    subprocess.run('pacman -Syu && mkinitcpio -P && update-grub', stdout=subprocess.PIPE, encoding='utf-8', shell=True)

def set_branch(branch_name):
    subprocess.run(f'pacman-mirrors --api --set-branch {branch_name} && pacman-mirrors --fasttrack 5 && pacman -Syyu', shell=True)

def reinstall_al_packages():
    subprocess.run('pacman -Qnq | pacman -S -', shell=True)

class Info:

    @staticmethod
    def get_branch():
        p = subprocess.run('cat /etc/pacman-mirrors.conf | grep "Branch ="', stdout=subprocess.PIPE, encoding='utf-8',
                           shell=True)
        output = p.stdout.replace("Branch = ", "").strip()
        return output.capitalize()

    @staticmethod
    def get_desktop_session():
        return os.environ.get('DESKTOP_SESSION')

    @staticmethod
    def get_release():
        p = subprocess.run(['lsb_release', '-rd'], stdout=subprocess.PIPE, encoding='utf-8')
        return p.stdout

    @staticmethod
    def get_sys_info():
        p = subprocess.run(['inxi', '-MABcIG'], stdout=subprocess.PIPE, encoding='utf-8')
        return p.stdout

    @staticmethod
    def get_aur_packages():
        p = subprocess.run(['pacman', '-Qm'], stdout=subprocess.PIPE, encoding='utf-8')
        if p.stdout == "":
            return "None installed"
        else:
            return p.stdout


class Window(Gtk.Window):


    def __init__(self):

        Gtk.Window.__init__(self)
        self.set_border_width(10)
        self.set_resizable(False)
        self.set_default_size(800, 700)
        header = Gtk.HeaderBar(show_close_button=True, title="Manjaro Maintenance")
        self.set_titlebar(header)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_icon_from_file('/usr/share/icons/manjaro/maia/48x48.png')
        grid = Gtk.Grid()
        
        self.add(grid)
        branch_label = Gtk.Label(label="If you don't know what this is leave it on Stable, Testers Only.")
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(10)
        grid.attach(separator, 0, 2, 4, 1)
        grid.attach(branch_label, 0, 1, 1, 1)

        iter = 1
        button = Gtk.RadioButton.new_with_label_from_widget(None, branch[0])
        for btn in branch:
            button.set_margin_start(0)
            if iter != 1:
              button = Gtk.RadioButton.new_with_mnemonic_from_widget(button, btn)

            if btn == Info.get_branch():
                button.set_active(button)

            if iter == 1:
                self.stable = button
                button.set_tooltip_text("Stable packages are meant for GENERAL usage, and have gone through a couple of weeks being tested. These packages are usually free of any problems.")
            elif iter == 2:
                self.testing = button
                button.set_tooltip_text("WARNING - Testing packages could potentially still have problems.")
            elif iter == 3:
                self.unstable = button
                button.set_tooltip_text("DANGER - Unstable packages may consequently break your system!, Only meant for SKILLED users")

            grid.attach(button, iter, 1, 1, 1)
            button.connect("toggled", self.on_confirm)

            iter += 1

        scroll = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        grid.attach(scroll, 0, 3, 4, 2)
        label = Gtk.Label(label=
        f"\nSystem Information:\n{Info.get_release()}Desktop: {Info.get_desktop_session()}\n\nAUR Packages: ( Can cause instability in your system. )\n{Info.get_aur_packages()}\n\n{Info.get_sys_info()}")
        scroll.add(label)

        button = Gtk.Button.new_with_label("Fix Issues")
        button.connect("clicked", self.on_click)
        header.add(button)

        self.popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        for btn in issues:
            button = Gtk.ModelButton()
            button.set_label(btn)
            button.connect("clicked", self.on_confirm)
            vbox.pack_start(button, True, True, 4)
               
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

    def on_confirm(self, widget):
        btn = widget.get_label()
        sure = ", are you sure?"

        def init_dialog(msg):
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, "Confirm Action")
            dialog.format_secondary_text(msg)
            response = dialog.run()
            if response == Gtk.ResponseType.YES:
                if btn in branch:
                  for b in branch:
                    if b == btn:
                        # set_branch(btn)
                        print(f"set {btn}")

                elif btn == "Reinstall All Packages":
                    # reinstall_al_packages()
                    print(issues[0])

                elif btn == "Reinstall Keyrings":
                    # Todo Reinstall Keyrings
                    print(issues[1])

                elif btn == "Rebuild Initramfs":
                    # rebuild_kernel()
                    print(issues[2])

            elif response == Gtk.ResponseType.NO:
                branch_btn = (self.stable, self.testing, self.unstable)
                for b in branch_btn:
                  label = b.get_label()
                  if label == Info.get_branch():
                      b.set_active(self)

            dialog.destroy()

        if btn in branch:
            for b in branch:
                if b == btn:
                    active = widget.get_active()
                    if active:
                        if btn != Info.get_branch():
                            msg = f"Changing Branch to {btn}{sure}"
                            init_dialog(msg)

        elif btn in issues:
            msg = f"{btn}{sure}"
            init_dialog(msg)

    def on_click(self, button):
        self.popover.set_relative_to(button)
        self.popover.show_all()
        self.popover.popup()

w = Window()
w.connect("destroy", Gtk.main_quit)
w.show_all()
Gtk.main()