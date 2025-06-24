/* Speaker Color Admin JavaScript
 * Handles RGBA color picker with alpha sliders and applies colors to speaker shape
 * Simplified approach focusing on color application rather than real-time updates
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSpeakerColorAdmin();
});

function initializeSpeakerColorAdmin() {
    // Add alpha display spans next to sliders
    addAlphaDisplays();
    
    // Initialize color change listeners
    setupColorChangeListeners();
    
    // Apply colors to existing shape after a delay to let LeafletGeoAdmin load
    setTimeout(function() {
        applyColorsToShape();
    }, 2000);
    
    // Also try after an even longer delay in case the map takes time to load
    setTimeout(function() {
        applyColorsToShape();
    }, 5000);
}

function addAlphaDisplays() {
    // Add display spans for alpha values
    const fillAlphaInput = document.getElementById('id_fill_color_alpha');
    const borderAlphaInput = document.getElementById('id_border_color_alpha');
    
    if (fillAlphaInput) {
        const fillDisplay = document.createElement('span');
        fillDisplay.id = 'fill_alpha_display';
        fillDisplay.style.cssText = 'margin-left: 10px; font-weight: bold; color: #666;';
        fillDisplay.textContent = `(${fillAlphaInput.value}/255)`;
        fillAlphaInput.parentNode.appendChild(fillDisplay);
    }
    
    if (borderAlphaInput) {
        const borderDisplay = document.createElement('span');
        borderDisplay.id = 'border_alpha_display';
        borderDisplay.style.cssText = 'margin-left: 10px; font-weight: bold; color: #666;';
        borderDisplay.textContent = `(${borderAlphaInput.value}/255)`;
        borderAlphaInput.parentNode.appendChild(borderDisplay);
    }
}

function updateAlphaDisplay(slider, displayId) {
    const display = document.getElementById(displayId);
    if (display) {
        const percentage = Math.round((slider.value / 255) * 100);
        display.textContent = `(${slider.value}/255 - ${percentage}%)`;
    }
    
    // Apply colors when alpha changes
    setTimeout(function() {
        applyColorsToShape();
    }, 100);
}

function setupColorChangeListeners() {
    // Listen for changes to color and alpha inputs
    const colorInputs = [
        'id_fill_color_rgb',
        'id_fill_color_alpha', 
        'id_border_color_rgb',
        'id_border_color_alpha'
    ];
    
    colorInputs.forEach(function(inputId) {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('input', function() {
                updateHiddenFields();
                setTimeout(function() {
                    applyColorsToShape();
                }, 100);
            });
            input.addEventListener('change', function() {
                updateHiddenFields();
                setTimeout(function() {
                    applyColorsToShape();
                }, 100);
            });
        }
    });
}

function updateHiddenFields() {
    // Update the hidden fill_color field
    const fillRgb = document.getElementById('id_fill_color_rgb');
    const fillAlpha = document.getElementById('id_fill_color_alpha');
    const fillColorField = document.getElementById('id_fill_color');
    
    if (fillRgb && fillAlpha && fillColorField) {
        const alphaHex = parseInt(fillAlpha.value).toString(16).padStart(2, '0').toUpperCase();
        fillColorField.value = fillRgb.value + alphaHex;
    }
    
    // Update the hidden border_color field
    const borderRgb = document.getElementById('id_border_color_rgb');
    const borderAlpha = document.getElementById('id_border_color_alpha');
    const borderColorField = document.getElementById('id_border_color');
    
    if (borderRgb && borderAlpha && borderColorField) {
        const alphaHex = parseInt(borderAlpha.value).toString(16).padStart(2, '0').toUpperCase();
        borderColorField.value = borderRgb.value + alphaHex;
    }
}

function applyColorsToShape() {
    // Get current color values
    const fillRgb = document.getElementById('id_fill_color_rgb');
    const fillAlpha = document.getElementById('id_fill_color_alpha');
    const borderRgb = document.getElementById('id_border_color_rgb');
    const borderAlpha = document.getElementById('id_border_color_alpha');
    
    if (!fillRgb || !fillAlpha || !borderRgb || !borderAlpha) {
        return;
    }
    
    // Convert to RGBA for CSS
    const fillRgba = hexToRgba(fillRgb.value, fillAlpha.value);
    const borderRgba = hexToRgba(borderRgb.value, borderAlpha.value);
    
    // Find and update the shape map
    const shapeMap = findShapeMap();
    
    if (shapeMap) {
        updateShapeMapColors(shapeMap, fillRgba, borderRgba);
        addColorIndicatorToShapeField(fillRgba, borderRgba);
    } else {
        // Fallback: try to apply styles via CSS
        applyCSSColorOverrides(fillRgba, borderRgba);
    }
}

function findShapeMap() {
    // Look for leaflet containers
    const leafletContainers = document.querySelectorAll('.leaflet-container');
    
    for (let i = 0; i < leafletContainers.length; i++) {
        const container = leafletContainers[i];
        
        if (container._leaflet_map) {
            const map = container._leaflet_map;
            
            // Check if this map has any polygon layers
            let hasPolygons = false;
            map.eachLayer(function(layer) {
                if (layer instanceof L.Polygon || layer instanceof L.Rectangle || 
                    layer instanceof L.Circle || layer instanceof L.Path) {
                    hasPolygons = true;
                }
            });
            
            if (hasPolygons) {
                return map;
            }
        }
    }
    
    // Try global variables
    if (typeof window.map !== 'undefined' && window.map) {
        return window.map;
    }
    
    return null;
}

function hexToRgba(hex, alpha) {
    // Convert hex to RGB
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    const a = alpha / 255;
    
    return `rgba(${r}, ${g}, ${b}, ${a})`;
}

function updateShapeMapColors(map, fillColor, borderColor) {
    let layersUpdated = 0;
    
    // Update all existing polygon/shape layers
    map.eachLayer(function(layer) {
        // Check if this is a shape layer
        if (layer instanceof L.Polygon || 
            layer instanceof L.Rectangle || 
            layer instanceof L.Circle ||
            layer instanceof L.Path) {
            
            // Skip tile layers and markers
            if (layer instanceof L.TileLayer || layer instanceof L.Marker) {
                return;
            }
            
            try {
                layer.setStyle({
                    fillColor: fillColor,
                    color: borderColor,
                    fillOpacity: 1.0,  // Let the RGBA handle opacity
                    opacity: 1.0,
                    weight: 3  // Border thickness
                });
                layersUpdated++;
            } catch (e) {
                // Silently handle errors
            }
        }
    });
    
    // Also check for editable layers or feature groups
    if (map.editableLayers) {
        map.editableLayers.eachLayer(function(layer) {
            if (layer.setStyle && typeof layer.setStyle === 'function') {
                try {
                    layer.setStyle({
                        fillColor: fillColor,
                        color: borderColor,
                        fillOpacity: 1.0,
                        opacity: 1.0,
                        weight: 3
                    });
                    layersUpdated++;
                } catch (e) {
                    // Silently handle errors
                }
            }
        });
    }
}

function applyCSSColorOverrides(fillColor, borderColor) {
    // Create or update a style element with color overrides
    let styleElement = document.getElementById('speaker-color-override');
    
    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'speaker-color-override';
        document.head.appendChild(styleElement);
    }
    
    styleElement.innerHTML = `
        /* Speaker color overrides */
        .leaflet-container .leaflet-interactive {
            fill: ${fillColor} !important;
            stroke: ${borderColor} !important;
            stroke-width: 3px !important;
        }
        
        .leaflet-container path.leaflet-interactive {
            fill: ${fillColor} !important;
            stroke: ${borderColor} !important;
            stroke-width: 3px !important;
        }
        
        .leaflet-container svg path {
            fill: ${fillColor} !important;
            stroke: ${borderColor} !important;
            stroke-width: 3px !important;
        }
    `;
}

function addColorIndicatorToShapeField(fillColor, borderColor) {
    // Add a small color indicator next to the shape field label
    const shapeFieldContainer = document.querySelector('.field-shape');
    if (!shapeFieldContainer) return;
    
    let indicator = shapeFieldContainer.querySelector('.shape-color-indicator');
    
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.className = 'shape-color-indicator';
        indicator.style.cssText = `
            display: inline-block;
            margin-left: 10px;
            vertical-align: middle;
        `;
        
        const label = shapeFieldContainer.querySelector('label');
        if (label) {
            label.appendChild(indicator);
        }
    }
    
    indicator.innerHTML = `
        <span style="
            display: inline-block;
            width: 20px;
            height: 12px;
            background: ${fillColor};
            border: 2px solid ${borderColor};
            border-radius: 2px;
            margin-right: 5px;
            vertical-align: middle;
        "></span>
        <span style="font-size: 11px; color: #666;">Preview</span>
    `;
}

// Make updateAlphaDisplay globally available for inline handlers
window.updateAlphaDisplay = updateAlphaDisplay; 