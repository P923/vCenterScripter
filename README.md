<h1 align="center">
  <div ALIGN="center">
    <img alt="" src="https://github.com/P923/vCenterScripter/blob/main/vcs.png?raw=true" width="550px" height="359px" />
  </div>
  <br /><br />
  vCenterScripter</h1>
<p align="center">Python vCenter Helper</p>
<div align="center"><a href="https://www.python.org/"><img alt="@Python" src="https://camo.githubusercontent.com/b764d47c4b030ecf374353eddc2c5323c7e3cb45823b5f26e49b322c0fa89567/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f507974686f6e2d322e37253243253230332e352d3337373661622e7376673f6d61784167653d32353932303030" /></a>
</div><br />

### Introduction
<div>
    <p align="justify">
        vCenterScripter is a Python library designed to simplify and enhance the usage of the PyVMOMI library.
        vCenterScripter provides developers with an intuitive and streamlined interface, enabling them to automate and interact with VMware vSphere infrastructure effortlessly.
    </p>
</div>



### Prerequisites
```
pyvmomi
```


### Installing

```
pip install -e git+https://github.com/P923/vCenterScripter.git#egg=vcenterscripter
```


### Usage
An example of usage. 
```python
from vCenterScripter import vm

if __name__ == '__main__':
    si = connect.SmartConnect(host=args.host, user=args.user, pwd=args.pwd,
                              disableSslCertValidation=True)

    # Get names of VMs
    name_vms = list_vm_names(si)

    # Get a VM from vCenter
    vm = get_vm(si, "vm_name")

    # Run a program on VM using vmWare tools
    cred = vim.vm.guest.NamePasswordAuthentication(username=entry.username, password=entry.password)
    run_program(si, vm, cred, "net.exe", program_arguments="user")

    # Generate a snapshot
    generate_snapshot(si, vm, "Snapshot1", "A generated snapshot.")
    
    # And more...
```
For more documentation see the docstrings. 


## License
This project is licensed under the MIT License.


## Author
<a href="https://github.com/P923" title="P923">Matteo P923</a> | 2023

