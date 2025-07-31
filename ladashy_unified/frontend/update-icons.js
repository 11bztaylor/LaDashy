// Temporary fix: Update all icon displays to show emoji when image fails
document.addEventListener('DOMContentLoaded', function() {
    // Override image error handling
    document.body.addEventListener('error', function(e) {
        if (e.target.tagName === 'IMG' && e.target.classList.contains('service-icon-img')) {
            // Get service name from alt attribute
            const serviceName = e.target.alt;
            const emoji = getServiceIconEmoji(serviceName);
            
            // Replace image with emoji
            const emojiSpan = document.createElement('span');
            emojiSpan.style.fontSize = '1.5em';
            emojiSpan.textContent = emoji;
            e.target.parentNode.replaceChild(emojiSpan, e.target);
        }
    }, true);
});
