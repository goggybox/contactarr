
// -----------------------------contactarr------------------------------
// This file is part of contactarr
// Copyright (C) 2025 goggybox https://github.com/goggybox

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// that this program is licensed under. See LICENSE file. If not
// available, see <https://www.gnu.org/licenses/>.

// Please keep this header comment in all copies of the program.
// --------------------------------------------------------------------

class UserListSelector {
    /**
     * VISUAL EXPLANATION OF THE CLASS:
     * <div id="container-selector" <-- `containerId`
     *      <div id="list-of-admins">  <-- taken from `containerId`, removing '-selector' suffix
     *          <div class="user-container">Admin 1</div>
     *          <div class="remove-button">-</div>
     *      </div>
     * </div>
     */
    
    /**
     * @param {string} containerId is the string ID name container to which everything will be added.
     *      ^ EXPECTS NAME TO END IN '-selector'
     * @param {array} list is the list of users displayed as rows in the existing list.
     *      ^ EACH USER IS EXPECTED TO HAVE A username AND friendly_name FIELD.
     * @param {array} allOptions is the full pool of users that is shown in the dropdown.
     *      ^ the dropdown will exclude any user from this pool that is already in `list`
     *      ^ EACH USER IS EXPECTED TO HAVE A username AND friendly_name FIELD..
     * @param {function} onChange a callback function that runs when the list changes (add or remove).
     *      ^ receives the updated `list` AFTER the change as an argument.
     * @param {string} dropdownId the string ID name for the dropdown element.
     *      ^ defaults to `${containerId}-dropdown` if not provided
     */
    constructor(containerId, list, allOptions, onChange, dropdownId=null) {
        this.containerId = containerId;
        this.list = list;
        this.allOptions = allOptions;
        this.onChange = onChange;
        this.dropdownId = dropdownId ?? `${containerId}-dropdown`;
        this.isDropdownOpen = false;

        this.init();
    }

    init() {
        this.container = document.getElementById(this.containerId);
        this.container.innerHTML = "";

        this.renderList();
        this.initAddRow();
        this.initDropdown();
    }

    renderList() {
        if (this.list.length === 0) { return; }

        const selectorList = cr("div", "selector-list", `list-of-${this.containerId.replace('-selector', '')}`);
        this.list.forEach((item, idx) => {
            const userContainer = cr("div", "user-container");
            if (idx === this.list.length - 1) { userContainer.classList.add("last"); }

            const friendlyname = cr("p");
            friendlyname.textContent = item.friendly_name;
            friendlyname.style.fontWeight = '600';
            userContainer.appendChild(friendlyname);

            const username = cr("p");
            username.textContent = `(${item.username})`;
            userContainer.appendChild(username);
            selectorList.appendChild(userContainer);

            const removeButton = cr("div", "remove-button");
            if (idx === this.list.length - 1) { removeButton.classList.add("last"); }
            const p = cr("p");
            p.textContent = "-";
            removeButton.appendChild(p);

            removeButton.addEventListener("click", () => {
                this.list.splice(idx, 1);
                this.refresh();
                this.onChange?.(this.list);
            });
            selectorList.appendChild(removeButton);
        });

        this.container.appendChild(selectorList);
    }

    initAddRow() {
        const existingAddRow = document.getElementById(`add-row-${this.containerId}`);
        if (existingAddRow) { existingAddRow.remove(); }

        const addRow = cr("div", "add-row", `add-row-${this.containerId}`);
        if (this.isDropdownOpen) { addRow.classList.add("bottom-shadow"); }

        const p = cr("p", "add-text");
        p.textContent = "Add...";
        addRow.appendChild(p);

        const dropdownButton = cr("div", "dropdown-button");
        const dropdownChevron = cr("p", "dropdown-chevron");
        dropdownChevron.textContent = this.isDropdownOpen ? "⌃" : "⌄";
        if (this.isDropdownOpen) { dropdownChevron.classList.add("dropdown"); }
        dropdownButton.appendChild(dropdownChevron);

        dropdownButton.addEventListener("click", () => {
            this.isDropdownOpen = !this.isDropdownOpen;
            this.container.classList.toggle("dropdown");
            const dropdown = document.getElementById(this.dropdownId);
            if (dropdown) { dropdown.classList.toggle("dropdown"); }
            // Re-render to update chevron and shadow states
            this.initAddRow();
            this.initDropdown();
        });

        addRow.appendChild(dropdownButton);
        this.container.appendChild(addRow);
    }

    initDropdown() {
        const oldDropdown = document.getElementById(this.dropdownId);
        if (oldDropdown) { oldDropdown.remove(); }

        const dropdown = cr("div", "user-dropdown", this.dropdownId);
        if (this.isDropdownOpen) { dropdown.classList.add("dropdown"); }
        this.container.appendChild(dropdown);

        const existingUsernames = this.list.map(u => u.username);
        const options = this.allOptions.filter(u => !existingUsernames.includes(u.username));

        options.forEach((user, idx) => {
            const userContainer = cr("div", "user-container");
            if (idx === options.length - 1) { userContainer.classList.add("last"); }
            
            const name = cr("p");
            name.textContent = user.friendly_name;
            name.style.fontWeight = "600";
            userContainer.appendChild(name);

            const username = cr("p");
            username.textContent = `(${user.username})`;
            userContainer.appendChild(username);
            dropdown.appendChild(userContainer);

            const addButton = cr("div", "add-button");
            const plus = cr("p");
            plus.textContent = "+";
            addButton.appendChild(plus);
            dropdown.appendChild(addButton);
            
            addButton.addEventListener("click", () => {
                this.list.push(user);
                this.refresh();
                this.onChange?.(this.list);
                // Scroll to bottom to show new item
                const listElem = document.getElementById(`list-of-${this.containerId.replace('-selector', '')}`);
                if (listElem) {
                    listElem.scrollTo(0, listElem.scrollHeight);
                }
            });
        });
    }

    refresh() {
        this.init();
    }

    reset(newList) {
        this.list = [...newList];
        this.isDropdownOpen = false;
        this.init();
    }
}