# Changelog

Notable changes to Optimization Techniques are documented here.

## [0.2.2]

### Changed
- Refactored Graphical Method state persistence into `GraphicalPageMixin`.
- Centralized settings storage to preserve Graphical Method and Simplex Method data in a shared JSON file.
- Improved settings updates to prevent one method from overwriting the other's saved data.

### Added
- Support for migrating legacy Graphical Method settings to the new format.

### Fixed
- Corrected constraint widget validation during state restoration.

## [0.2.1]

### Added
- Simplex iteration table.

## [0.2.0]

### Changed
- Removed unused code and cleaned up the project structure.

## [0.1.0]

### Added
- Initial project version.
- Graphical Method for two-variable linear programming.
- Sidebar navigation between optimization methods.
- Initial Simplex Method interface and solver integration.
- Automatic saving of Graphical Method inputs.
- Separate modules for graphical and Simplex solvers.

## Planned

- Big M Method.
- Two-Phase Method.
- Transportation Problems.
- Step-by-step Simplex tableau visualization.