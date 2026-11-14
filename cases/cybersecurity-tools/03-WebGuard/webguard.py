import argparse
import json
import ssl
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

HEADERS = {
    'strict-transport-security': 'HSTS',
    'content-security-policy': 'CSP',
    'x-content-type-options': 'X-Content-Type-Options',
    'referrer-policy': 'Referrer-Policy',
    'permissions-policy': 'Permissions-Policy',
    'x-frame-options': 'X-Frame-Options (legacy)',
}


def inspect_response(url, final_url, status, headers):
    secure = urlsplit(final_url).scheme.lower() == 'https'
    result = {
        'url': url, 'status': status, 'final_url': final_url,
        'https': secure, 'headers': {}, 'findings': [],
    }
    for key, label in HEADERS.items():
        value = headers.get(key, '')
        present = bool(value.strip())
        result['headers'][key] = {'present': present, 'value': value}
        if not present and (key != 'strict-transport-security' or secure):
            result['findings'].append({
                'severity': 'medium' if key in ('strict-transport-security', 'content-security-policy') else 'low',
                'finding': f'Missing {label} header',
            })
    if not secure:
        result['findings'].append({'severity': 'high', 'finding': 'Final URL does not use HTTPS'})
    # Every Set-Cookie must be checked independently; a flag on one cookie does not protect another.
    for index, cookie in enumerate(headers.get_all('Set-Cookie', []), start=1):
        attributes = {part.strip().split('=', 1)[0].lower() for part in cookie.split(';')[1:]}
        if secure and 'secure' not in attributes:
            result['findings'].append({'severity': 'medium', 'finding': f'Cookie #{index} missing Secure'})
        if 'httponly' not in attributes:
            result['findings'].append({'severity': 'low', 'finding': f'Cookie #{index} missing HttpOnly (may be intentional)'})
    result['checked_at'] = datetime.now(timezone.utc).isoformat()
    return result


def inspect_url(url, timeout=8):
    parsed = urlsplit(url)
    if parsed.scheme.lower() not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Expected an http(s) URL with a hostname and no embedded credentials')
    if timeout <= 0 or timeout > 60:
        raise ValueError('timeout must be between 0 and 60 seconds')
    request = Request(url, headers={'User-Agent': 'WebGuard/1.0 (authorized configuration audit)'})
    try:
        with urlopen(request, timeout=timeout, context=ssl.create_default_context()) as response:
            return inspect_response(url, response.geturl(), response.status, response.headers)
    except HTTPError as exc:
        # HTTP error responses still have useful headers to audit.
        return inspect_response(url, exc.geturl(), exc.code, exc.headers)


def main():
    parser = argparse.ArgumentParser(description='Check HTTP security headers on an authorized website.')
    parser.add_argument('url')
    parser.add_argument('--timeout', type=float, default=8)
    parser.add_argument('--json', type=Path)
    args = parser.parse_args()
    try:
        result = inspect_url(args.url, args.timeout)
    except (ValueError, URLError, TimeoutError, ssl.SSLError, OSError) as exc:
        parser.error(f'Request failed: {exc}')
    output = json.dumps(result, indent=2)
    print(output)
    if args.json:
        args.json.write_text(output + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
