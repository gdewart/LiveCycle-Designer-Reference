# LiveCycle Designer Programming Syntax

Quick reference for Adobe LiveCycle Designer 6.5.8 XFA scripting,  FormCalc and Javascript (ES3).

## Table of Contents

- [XFA Syntax Fundamentals](#xfa-syntax-fundamentals)
  - [Node Resolution & Value Access](#node-resolution--value-access)
  - [DOM Navigation & Event Handling](#dom-navigation--event-handling)
  - [Common XFA Operations](#common-xfa-operations)
- [FormCalc Scripting](#formcalc-scripting)
  - [Basic Syntax & Math Operations](#basic-syntax--math-operations)
  - [Strings, Dates & Logic](#strings-dates--logic)
  - [Practical Examples](#practical-examples)
- [Page Navigation & Layout Management](#page-navigation--layout-management)
  - [Page Operations](#page-operations)
  - [Subform Management](#subform-management)
  - [Layout Control](#layout-control)
- [Global Utility Functions](#global-utility-functions)
  - [Global Namespace](#global-namespace)
  - [Array Iteration](#array-iteration)
  - [Object Polyfills](#object-polyfills)
  - [Sorting Utilities](#sorting-utilities)
  - [Region & Location Helpers](#region--location-helpers)
  - [Dropdown & UI Utilities](#dropdown--ui-utilities)
  - [General Helpers & Validation](#general-helpers--validation)
  - [Render & Detail Logic](#render--detail-logic)
  - [Constants & Utilities](#constants--utilities)

---

## Quick Reference Summary

### Essential XFA Objects & Methods
- `xfa.resolveNode("path")` - Get node reference
- `this.rawValue` / `this.value` - Access field values
- `event.target.rawValue` / `event.value` - Event handling
- `xfa.host.messageBox("Text", "Title", 0)` - User dialogs
- `xfa.form.remerge()` - Refresh layout
- `console.println("Debug:", value)` - Debug output
- `fld.setFocus()` - Move focus to field
- `xfa.record` - Data model root access
- `xfa.host.numPages` - Get total page count
- `xfa.layout.pageContent(index, "field")` - Get page fields

### Essential FormCalc Syntax
- `$` - Current field shorthand
- `Field1 + Field2` - Simple arithmetic
- `Upper("text")`, `Lower("TEXT")`, `Len("text")` - String functions
- `Date()`, `Time()` - Current date/time
- `if...then...else...endif` - Conditional logic
- `Round(num, decimals)` - Number formatting
- `IsNum($)`, `IsDate($, "format")` - Validation functions
- `Substr("text", start, length)` - Substring extraction

### Common Field Properties
- `presence` - "visible" | "hidden" | "invisible"
- `mandatory` - "error" | "disabled"
- `borderColor` - RGB color string "255,0,0"
- `fillColor` - Background RGB color "255,255,0"
- `access` - "open" | "readOnly" | "protected"
- `rawValue` - Unformatted field value
- `assist.toolTip.value` - Tooltip text
- `assist.speak.value` - Screen reader text

### Dropdown Operations
- `clearItems()` - Clear all options
- `addItem("Label", "Value")` - Add new option
- `boundItem(index)` - Get value by index
- Focus with `setFocus()`

### Quick FormCalc Calculations
- `Subtotal * 0.08` - Calculate tax
- `Price * Percent / 100` - Percentage calculations
- `Floor((Date() - BirthDate) / 365.25)` - Age calculation
- `today + 30` - Date arithmetic (30 days from now)
- `Format(Round($, 2), "999,999.00")` - Currency formatting

### Event Types
- **Initialize** - Form/field initialization
- **Calculate** - Automatic calculations (FormCalc preferred)
- **Validate** - Field validation on exit
- **Change** - Value change detection
- **Exit** - Field exit events
- **Enter** - Field entry events

### Core Loops & Iteration
- **JavaScript:** `for (var i = 0; i < arr.length; i++)` - Standard loop
- **FormCalc:** `for i = 1 upto 10 do...endfor` - Range loop
- **Page Loop:** `for (var p = 0; p < xfa.host.numPages; p++)` - Page iteration

### Data Model Access
- **JavaScript:** `xfa.record.nodeName.value` - Data node access
- **FormCalc:** `$record.nodeName` - Data node shorthand
- **Datasets:** `xfa.datasets.data.Form.field` - Direct data access

### Null/Empty Checks
- **JavaScript:** `val != null && val !== ""` - Null/empty check
- **FormCalc:** `$ ne null and $ ne ""` - FormCalc null check
- **HasValue:** `Len(Ltrim(Rtrim($))) > 0` - Trimmed value check

---

## XFA Syntax Fundamentals

### Node Resolution & Value Access

```javascript
// Node references
var fld = xfa.resolveNode("form1.#subform.Page1.TextField1");  // Template DOM
var xml = xfa.datasets.data.Form.form1.Page1.TextField1;       // Data DOM

// Value access (both template and data DOM)
this.rawValue;                // unformatted value (get/set)
this.value;                   // formatted/display value
this.getRawValue();           // method to get raw value
this.setRawValue("New");      // method to set raw value
xml.setRawValue("DataVal");   // data DOM set method
```

### DOM Navigation & Event Handling

```javascript
// Navigation patterns
this.parent;                           // parent access
$parent.TextField1;                    // sibling via parent  
this.TextField1;                       // direct child
this.resolveNode("TextField1");        // dynamic child
$template, $data, $record;             // root references

// Dynamic navigation
var field = this.parent.resolveNode("Field" + counter);
var node = this; while (node.parent) { node = node.parent; } // walk up

// Event handling
event.target.rawValue;                 // target field in events
event.value;                           // current event value
```

### Common XFA Operations

```javascript
// Dialogs & layout
xfa.host.messageBox("Text", "Title", 0);  // 0=OK, 1=YesNo, 2=OKCancel
xfa.host.response;                        // last dialog result
xfa.form.remerge();                       // refresh layout
this.setFocus();                          // move focus to field

// Field properties
fld.presence = "visible";                 // "visible"|"hidden"|"invisible"
fld.mandatory = "error";                  // "error"|"disabled"
fld.access = "readOnly";                  // "open"|"readOnly"|"protected"

// Debug output
console.println("DEBUG:", this.rawValue);
```

---

## FormCalc Scripting

Adobe's calculation language for form calculations - simpler than JavaScript for math operations.

### Basic Syntax & Math Operations

```formcalc
// Variables & field assignment
var myValue = 10; var myText = "Hello"; $ = 100  // $ = current field shorthand
/* comments */ // single line comments

// Arithmetic & math functions  
var total = Field1 + Field2 + Field3; var percentage = (Field1 / Field2) * 100
Abs(-5), Ceil(4.3), Floor(4.7), Round(4.567, 2), Max(1,5,3), Min(1,5,3), Sqrt(16)
```

### Strings, Dates & Logic

```formcalc
// String operations
var fullName = FirstName + " " + LastName  // concatenation
Len("text"), Upper("text"), Lower("TEXT"), Substr("Hello World", 7, 5)
Left("Hello", 3), Right("Hello", 3), Replace("old", "old", "new")
Ltrim("  text"), Rtrim("text  "), At("text", "search") // position or 0

// Date/time operations  
var today = Date(); var now = Time(); var age = Floor((Date() - BirthDate) / 365.25)
Date2Str(today, "MM/DD/YYYY"), Time2Str(now, "HH:MM:SS")
Year(today), Month(today), Day(today)  // date parts

// Conditionals & validation
if (Field1 > 100) then Field2 = "High" else Field2 = "Low" endif
IsNum($), IsDate($, "MM/DD/YYYY")  // validation functions
for i = 1 upto 10 do Total = Total + Ref("Item" + Str(i)) endfor  // loops
```

### Practical Examples

```formcalc
// Field references & navigation
var value = TextField1; var sibling = $parent.OtherField
var dynamic = Ref("Field" + Str(counter)); $ = 100  // set current field

// Financial calculations
var tax = Subtotal * 0.08; var discount = Price * DiscountPct / 100
var total = Subtotal + tax - discount

// Validation & formatting
if (IsNum($) and $ >= 0 and $ <= 100) then Grade = "Valid" endif
var phone = "(" + Substr($,1,3) + ") " + Substr($,4,3) + "-" + Substr($,7,4)
var currency = "$" + Format(Round($, 2), "999,999.00")

// Advanced patterns
var grade = Choose(Ceil(Score/10), "F","F","F","F","F","F","D","C","B","A","A")
if (Len(Ltrim(Rtrim($))) eq 0) then xfa.host.messageBox("Required field") endif
```

---

## Page Navigation & Layout Management

### Page Operations

**Get page count:**
```javascript
var pageCount = xfa.host.numPages;
```

**Navigate to specific page:**
```javascript
xfa.host.currentPage = 2; // Go to page 2 (0-based)
```

**Get fields on specific page:**
```javascript
var pageFields = xfa.layout.pageContent(0, "field");
for (var i = 0; i < pageFields.length; i++) {
    var field = pageFields.item(i);
    console.println("Field:", field.name);
}
```

### Subform Management

**Show/hide subforms:**
```javascript
// Hide subform
xfa.resolveNode("form1.#subform.DetailSection").presence = "hidden";

// Make subform invisible (takes space but not visible)
xfa.resolveNode("form1.#subform.DetailSection").presence = "invisible";
```

**Add/remove subform instances:**
```javascript
// Add new instance
var newInstance = xfa.resolveNode("form1.#subform.RepeatingSection").instanceManager.addInstance(1);

// Remove instance
xfa.resolveNode("form1.#subform.RepeatingSection").instanceManager.removeInstance(0);

// Get instance count
var count = xfa.resolveNode("form1.#subform.RepeatingSection").instanceManager.count;
```

### Layout Control

**Force layout recalculation:**
```javascript
xfa.form.remerge();
xfa.layout.relayout();
```

**Get field coordinates:**
```javascript
var field = xfa.resolveNode("form1.#subform.TextField1");
var x = field.x.value;
var y = field.y.value;
var width = field.w.value;
var height = field.h.value;
```

---

## Global Utility Functions

### Global Namespace

```javascript
var formUtils = formUtils || {};
```

### Array Iteration

Populate dropdown with array data:

```javascript
var arr = ["Option A", "Option B", "Option C"];
var dropdownOne = this; // if script is inside dropdown, otherwise reference full path

dropdownOne.clearItems();

for (var i = 0; i < arr.length; i++) {
    dropdownOne.addItem(arr[i]);
}
```

### Object Polyfills

**Object.keys polyfill** - Returns an array of an object's own enumerable property names:

```javascript
if (typeof Object.keys !== "function") {
  Object.keys = function(obj) {
    var result = [];
    for (var k in obj) {
      if (obj.hasOwnProperty(k)) {
        result.push(k);
      }
    }
    return result;
  };
}
```

**Object.values polyfill** - Returns an array of an object's own enumerable property values:

```javascript
formUtils.keys = function(o) {
  var ks = [];
  for (var k in o) {
    if (o.hasOwnProperty(k)) ks.push(k);
  }
  return ks;
};
```

**Object.entries polyfill** - Returns an array of an object's own enumerable key, value pairs:

```javascript
if (typeof Object.entries !== "function") {
  Object.entries = function(obj) {
    var result = [];
    for (var k in obj) {
      if (obj.hasOwnProperty(k)) {
        result.push([k, obj[k]]);
      }
    }
    return result;
  };
}
```

### Sorting Utilities

Sort an array (default: alphabetical):

```javascript
formUtils.sortArray = function(arr, comparator) {
  var cmp = comparator || function(a, b) {
    return a < b ? -1 : (a > b ? 1 : 0);
  };
  return arr.sort(cmp);
};
```

### Region & Location Helpers

**Get all top-level region keys:**

```javascript
formUtils.getRegionKeys = function() {
  var ks = formUtils.keys(Locations);
  return formUtils.sortArray(ks);
};
```

**Get sorted location entries for a given region:**

```javascript
formUtils.getLocationEntries = function(regionKey) {
  var list = [], bucket = Locations[regionKey] || {};
  for (var k in bucket) {
    if (bucket.hasOwnProperty(k)) {
      list.push({ key: k, data: bucket[k] });
    }
  }
  formUtils.sortArray(list, function(a, b) {
    return a.key.localeCompare(b.key);
  });
  return list;
};
```

### Dropdown & UI Utilities

**Clear all items from a dropdown:**

```javascript
formUtils.clearDropdown = function(dropdownField) {
  dropdownField.clearItems();
};
```

**Populate a dropdown from a key–label map:**

```javascript
formUtils.populateDropdown = function(dropdownField, map) {
  formUtils.clearDropdown(dropdownField);
  var keys = formUtils.sortArray(formUtils.keys(map));
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    dropdownField.addItem(map[key], key);
  }
};
```

**Toggle visibility of a node:**

```javascript
formUtils.toggleVisible = function(node, show) {
  node.presence = show ? "visible" : "hidden";
};
```

**Set mandatory field status:**

```javascript
formUtils.setMandatory = function(node, isRequired) {
  node.mandatory = isRequired ? "error" : "disabled";
};
```

### General Helpers & Validation

**Check if a value is non-null and non-empty:**

```javascript
formUtils.hasValue = function(val) {
  return val != null && val !== "";
};
```

**Validate a field with optional rules:**

```javascript
formUtils.validateField = function(field, options) {
  var val = field.rawValue, isValid = true, msg = "";

  if (options.required && !formUtils.hasValue(val)) {
    isValid = false;
    msg = options.requiredMessage || "This field is required.";
  }

  if (isValid && options.pattern && formUtils.hasValue(val)) {
    if (!options.pattern.test(val)) {
      isValid = false;
      msg = options.patternMessage || "Invalid format.";
    }
  }

  if (isValid && options.minLength && formUtils.hasValue(val)) {
    if (val.length < options.minLength) {
      isValid = false;
      msg = options.minLengthMessage || "Too short.";
    }
  }

  if (isValid && options.maxLength && formUtils.hasValue(val)) {
    if (val.length > options.maxLength) {
      isValid = false;
      msg = options.maxLengthMessage || "Too long.";
    }
  }

  if (!isValid) {
    field.borderColor = formUtils.COLOR_REQUIRED;
    if (options.showAlert) xfa.host.messageBox(msg, "Validation Error");
  } else {
    field.borderColor = formUtils.COLOR_OK;
  }

  return isValid;
};
```

### Render & Detail Logic

**Populate detail fields using global variables:**

```javascript
formUtils.renderDetails = function() {
  var det = Locations[currentRegion][currentLocation];
  var nameFld  = xfa.resolveNode("form1.#subform.locationName");
  var regFld   = xfa.resolveNode("form1.#subform.locationRegion");
  var infoSec  = xfa.resolveNode("form1.#subform.infoSection");
  var codeFld  = xfa.resolveNode("form1.#subform.storeCode");

  nameFld.rawValue   = det.name.toUpperCase();
  regFld.rawValue    = det.region;
  codeFld.rawValue   = currentLocation;
  infoSec.presence   = det ? "visible" : "hidden";

  console.println("Region:", currentRegion, "| Location:", currentLocation);

  if (ScriptUtils && ScriptUtils.fetchStoreHours) {
    ScriptUtils.fetchStoreHours(currentLocation, function(hours) {
      xfa.resolveNode("form1.#subform.storeHours").rawValue = hours;
    });
  }

  xfa.form.remerge();
  xfa.resolveNode("form1.#subform.nextField").setFocus();
};
```

### Constants & Utilities

**Color constants for validation:**

```javascript
formUtils.COLOR_REQUIRED = "255,0,0";
formUtils.COLOR_OK       = "0,128,0";
```

**Shallow object clone:**

```javascript
formUtils.clone = function(obj) {
  var copy = {};
  for (var k in obj) {
    if (obj.hasOwnProperty(k)) copy[k] = obj[k];
  }
  return copy;
};
```

**Date helpers:**

```javascript
formUtils.getToday = function() {
  var d = new Date();
  return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate();
};

formUtils.daysBetween = function(d1, d2) {
  var dt1 = new Date(d1), dt2 = new Date(d2);
  var diff = Math.abs(dt2.getTime() - dt1.getTime());
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
};
```

---

## Contributing

Feel free to contribute to this cheatsheet by submitting pull requests with additional XFA scripting examples and best practices.
