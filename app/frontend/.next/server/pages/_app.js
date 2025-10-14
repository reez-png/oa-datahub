"use strict";
/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "pages/_app";
exports.ids = ["pages/_app"];
exports.modules = {

/***/ "./pages/_app.tsx":
/*!************************!*\
  !*** ./pages/_app.tsx ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react/jsx-dev-runtime */ \"react/jsx-dev-runtime\");\n/* harmony import */ var react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ \"react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var leaflet_dist_leaflet_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! leaflet/dist/leaflet.css */ \"./node_modules/leaflet/dist/leaflet.css\");\n/* harmony import */ var leaflet_dist_leaflet_css__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(leaflet_dist_leaflet_css__WEBPACK_IMPORTED_MODULE_2__);\n// pages/_app.tsx\n\n\n\nfunction Header() {\n    const [mounted, setMounted] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);\n    const [authed, setAuthed] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);\n    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(()=>{\n        setMounted(true);\n        const read = ()=>setAuthed(!!localStorage.getItem(\"sb-access-token\"));\n        read();\n        // stay in sync across tabs/windows\n        const onStorage = (e)=>{\n            if (e.key === \"sb-access-token\") read();\n        };\n        window.addEventListener(\"storage\", onStorage);\n        return ()=>window.removeEventListener(\"storage\", onStorage);\n    }, []);\n    const logout = ()=>{\n        localStorage.removeItem(\"sb-access-token\");\n        // hard redirect avoids hydration edge cases\n        window.location.href = \"/login\";\n    };\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"div\", {\n        style: {\n            padding: \"8px 16px\",\n            borderBottom: \"1px solid #eee\",\n            display: \"flex\",\n            gap: 12\n        },\n        children: [\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"a\", {\n                href: \"/\",\n                children: \"Datasets\"\n            }, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 38,\n                columnNumber: 7\n            }, this),\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"a\", {\n                href: \"/login\",\n                children: \"Login\"\n            }, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 39,\n                columnNumber: 7\n            }, this),\n            mounted && authed ? /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"button\", {\n                onClick: logout,\n                style: {\n                    marginLeft: \"auto\"\n                },\n                children: \"Logout\"\n            }, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 42,\n                columnNumber: 9\n            }, this) : /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(\"span\", {\n                style: {\n                    marginLeft: \"auto\"\n                }\n            }, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 46,\n                columnNumber: 9\n            }, this)\n        ]\n    }, void 0, true, {\n        fileName: \"/app/pages/_app.tsx\",\n        lineNumber: 30,\n        columnNumber: 5\n    }, this);\n}\nfunction App({ Component, pageProps }) {\n    return /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.Fragment, {\n        children: [\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Header, {}, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 55,\n                columnNumber: 7\n            }, this),\n            /*#__PURE__*/ (0,react_jsx_dev_runtime__WEBPACK_IMPORTED_MODULE_0__.jsxDEV)(Component, {\n                ...pageProps\n            }, void 0, false, {\n                fileName: \"/app/pages/_app.tsx\",\n                lineNumber: 56,\n                columnNumber: 7\n            }, this)\n        ]\n    }, void 0, true);\n}\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9wYWdlcy9fYXBwLnRzeCIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUEsaUJBQWlCOztBQUUyQjtBQUNWO0FBRWxDLFNBQVNFO0lBQ1AsTUFBTSxDQUFDQyxTQUFTQyxXQUFXLEdBQUdILCtDQUFRQSxDQUFDO0lBQ3ZDLE1BQU0sQ0FBQ0ksUUFBUUMsVUFBVSxHQUFHTCwrQ0FBUUEsQ0FBQztJQUVyQ0QsZ0RBQVNBLENBQUM7UUFDUkksV0FBVztRQUNYLE1BQU1HLE9BQU8sSUFBTUQsVUFBVSxDQUFDLENBQUNFLGFBQWFDLE9BQU8sQ0FBQztRQUNwREY7UUFFQSxtQ0FBbUM7UUFDbkMsTUFBTUcsWUFBWSxDQUFDQztZQUNqQixJQUFJQSxFQUFFQyxHQUFHLEtBQUssbUJBQW1CTDtRQUNuQztRQUNBTSxPQUFPQyxnQkFBZ0IsQ0FBQyxXQUFXSjtRQUNuQyxPQUFPLElBQU1HLE9BQU9FLG1CQUFtQixDQUFDLFdBQVdMO0lBQ3JELEdBQUcsRUFBRTtJQUVMLE1BQU1NLFNBQVM7UUFDYlIsYUFBYVMsVUFBVSxDQUFDO1FBQ3hCLDRDQUE0QztRQUM1Q0osT0FBT0ssUUFBUSxDQUFDQyxJQUFJLEdBQUc7SUFDekI7SUFFQSxxQkFDRSw4REFBQ0M7UUFDQ0MsT0FBTztZQUNMQyxTQUFTO1lBQ1RDLGNBQWM7WUFDZEMsU0FBUztZQUNUQyxLQUFLO1FBQ1A7OzBCQUVBLDhEQUFDQztnQkFBRVAsTUFBSzswQkFBSTs7Ozs7OzBCQUNaLDhEQUFDTztnQkFBRVAsTUFBSzswQkFBUzs7Ozs7O1lBRWhCaEIsV0FBV0UsdUJBQ1YsOERBQUNzQjtnQkFBT0MsU0FBU1o7Z0JBQVFLLE9BQU87b0JBQUVRLFlBQVk7Z0JBQU87MEJBQUc7Ozs7O3FDQUl4RCw4REFBQ0M7Z0JBQUtULE9BQU87b0JBQUVRLFlBQVk7Z0JBQU87Ozs7Ozs7Ozs7OztBQUkxQztBQUVlLFNBQVNFLElBQUksRUFBRUMsU0FBUyxFQUFFQyxTQUFTLEVBQVk7SUFDNUQscUJBQ0U7OzBCQUNFLDhEQUFDL0I7Ozs7OzBCQUNELDhEQUFDOEI7Z0JBQVcsR0FBR0MsU0FBUzs7Ozs7Ozs7QUFHOUIiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9vYS1mcm9udGVuZC8uL3BhZ2VzL19hcHAudHN4PzJmYmUiXSwic291cmNlc0NvbnRlbnQiOlsiLy8gcGFnZXMvX2FwcC50c3hcclxuaW1wb3J0IHR5cGUgeyBBcHBQcm9wcyB9IGZyb20gXCJuZXh0L2FwcFwiO1xyXG5pbXBvcnQgeyB1c2VFZmZlY3QsIHVzZVN0YXRlIH0gZnJvbSBcInJlYWN0XCI7XHJcbmltcG9ydCBcImxlYWZsZXQvZGlzdC9sZWFmbGV0LmNzc1wiO1xyXG5cclxuZnVuY3Rpb24gSGVhZGVyKCkge1xyXG4gIGNvbnN0IFttb3VudGVkLCBzZXRNb3VudGVkXSA9IHVzZVN0YXRlKGZhbHNlKTtcclxuICBjb25zdCBbYXV0aGVkLCBzZXRBdXRoZWRdID0gdXNlU3RhdGUoZmFsc2UpO1xyXG5cclxuICB1c2VFZmZlY3QoKCkgPT4ge1xyXG4gICAgc2V0TW91bnRlZCh0cnVlKTtcclxuICAgIGNvbnN0IHJlYWQgPSAoKSA9PiBzZXRBdXRoZWQoISFsb2NhbFN0b3JhZ2UuZ2V0SXRlbShcInNiLWFjY2Vzcy10b2tlblwiKSk7XHJcbiAgICByZWFkKCk7XHJcblxyXG4gICAgLy8gc3RheSBpbiBzeW5jIGFjcm9zcyB0YWJzL3dpbmRvd3NcclxuICAgIGNvbnN0IG9uU3RvcmFnZSA9IChlOiBTdG9yYWdlRXZlbnQpID0+IHtcclxuICAgICAgaWYgKGUua2V5ID09PSBcInNiLWFjY2Vzcy10b2tlblwiKSByZWFkKCk7XHJcbiAgICB9O1xyXG4gICAgd2luZG93LmFkZEV2ZW50TGlzdGVuZXIoXCJzdG9yYWdlXCIsIG9uU3RvcmFnZSk7XHJcbiAgICByZXR1cm4gKCkgPT4gd2luZG93LnJlbW92ZUV2ZW50TGlzdGVuZXIoXCJzdG9yYWdlXCIsIG9uU3RvcmFnZSk7XHJcbiAgfSwgW10pO1xyXG5cclxuICBjb25zdCBsb2dvdXQgPSAoKSA9PiB7XHJcbiAgICBsb2NhbFN0b3JhZ2UucmVtb3ZlSXRlbShcInNiLWFjY2Vzcy10b2tlblwiKTtcclxuICAgIC8vIGhhcmQgcmVkaXJlY3QgYXZvaWRzIGh5ZHJhdGlvbiBlZGdlIGNhc2VzXHJcbiAgICB3aW5kb3cubG9jYXRpb24uaHJlZiA9IFwiL2xvZ2luXCI7XHJcbiAgfTtcclxuXHJcbiAgcmV0dXJuIChcclxuICAgIDxkaXZcclxuICAgICAgc3R5bGU9e3tcclxuICAgICAgICBwYWRkaW5nOiBcIjhweCAxNnB4XCIsXHJcbiAgICAgICAgYm9yZGVyQm90dG9tOiBcIjFweCBzb2xpZCAjZWVlXCIsXHJcbiAgICAgICAgZGlzcGxheTogXCJmbGV4XCIsXHJcbiAgICAgICAgZ2FwOiAxMixcclxuICAgICAgfX1cclxuICAgID5cclxuICAgICAgPGEgaHJlZj1cIi9cIj5EYXRhc2V0czwvYT5cclxuICAgICAgPGEgaHJlZj1cIi9sb2dpblwiPkxvZ2luPC9hPlxyXG4gICAgICB7LyogUmVuZGVyIGFmdGVyIG1vdW50IHNvIFNTUiBhbmQgY2xpZW50IG1hdGNoICovfVxyXG4gICAgICB7bW91bnRlZCAmJiBhdXRoZWQgPyAoXHJcbiAgICAgICAgPGJ1dHRvbiBvbkNsaWNrPXtsb2dvdXR9IHN0eWxlPXt7IG1hcmdpbkxlZnQ6IFwiYXV0b1wiIH19PlxyXG4gICAgICAgICAgTG9nb3V0XHJcbiAgICAgICAgPC9idXR0b24+XHJcbiAgICAgICkgOiAoXHJcbiAgICAgICAgPHNwYW4gc3R5bGU9e3sgbWFyZ2luTGVmdDogXCJhdXRvXCIgfX0gLz5cclxuICAgICAgKX1cclxuICAgIDwvZGl2PlxyXG4gICk7XHJcbn1cclxuXHJcbmV4cG9ydCBkZWZhdWx0IGZ1bmN0aW9uIEFwcCh7IENvbXBvbmVudCwgcGFnZVByb3BzIH06IEFwcFByb3BzKSB7XHJcbiAgcmV0dXJuIChcclxuICAgIDw+XHJcbiAgICAgIDxIZWFkZXIgLz5cclxuICAgICAgPENvbXBvbmVudCB7Li4ucGFnZVByb3BzfSAvPlxyXG4gICAgPC8+XHJcbiAgKTtcclxufVxyXG4iXSwibmFtZXMiOlsidXNlRWZmZWN0IiwidXNlU3RhdGUiLCJIZWFkZXIiLCJtb3VudGVkIiwic2V0TW91bnRlZCIsImF1dGhlZCIsInNldEF1dGhlZCIsInJlYWQiLCJsb2NhbFN0b3JhZ2UiLCJnZXRJdGVtIiwib25TdG9yYWdlIiwiZSIsImtleSIsIndpbmRvdyIsImFkZEV2ZW50TGlzdGVuZXIiLCJyZW1vdmVFdmVudExpc3RlbmVyIiwibG9nb3V0IiwicmVtb3ZlSXRlbSIsImxvY2F0aW9uIiwiaHJlZiIsImRpdiIsInN0eWxlIiwicGFkZGluZyIsImJvcmRlckJvdHRvbSIsImRpc3BsYXkiLCJnYXAiLCJhIiwiYnV0dG9uIiwib25DbGljayIsIm1hcmdpbkxlZnQiLCJzcGFuIiwiQXBwIiwiQ29tcG9uZW50IiwicGFnZVByb3BzIl0sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///./pages/_app.tsx\n");

/***/ }),

/***/ "react":
/*!************************!*\
  !*** external "react" ***!
  \************************/
/***/ ((module) => {

module.exports = require("react");

/***/ }),

/***/ "react/jsx-dev-runtime":
/*!****************************************!*\
  !*** external "react/jsx-dev-runtime" ***!
  \****************************************/
/***/ ((module) => {

module.exports = require("react/jsx-dev-runtime");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/leaflet"], () => (__webpack_exec__("./pages/_app.tsx")));
module.exports = __webpack_exports__;

})();