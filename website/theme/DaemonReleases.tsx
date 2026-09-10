// Daemon release page: everything on it comes from the index.json that
// scripts/publish-aiod.sh writes next to the binaries, so a release shows up
// here the moment it is published and nothing is written by hand.
import { type ReactNode, useEffect, useState } from 'react';
import './DaemonReleases.css';

// The release store this page reads. Override per site: the public site must
// point at a publicly reachable mirror.
const DEFAULT_INDEX_URL = 'https://aio-static.tos-cn-beijing.volces.com/index.json';
const DEFAULT_LATEST_URL = 'https://aio-static.tos-cn-beijing.volces.com/latest/{path}';

type FileEntry = { bin: string; path: string; size: number; sha256: string };
type Artifact = { platform: string; os: string; arch: string; libc?: string; files: FileEntry[] };
type Manifest = {
  version: string;
  tag: string;
  channel: 'stable' | 'rc';
  date: string;
  changelog_date: string | null;
  source: { commit: string };
  build: Record<string, string | null>;
  notes: string;
  artifacts: Artifact[];
};
type Index = {
  generated: string;
  latest: { stable: string | null; rc: string | null };
  mirrors: { id: string; template: string }[];
  versions: Manifest[];
};

const TEXT = {
  en: {
    loading: 'Loading releases…',
    failed: 'Could not load the release index',
    latest: 'Latest',
    install: 'Install the latest daemon on Linux x86_64',
    downloads: 'Downloads',
    releases: 'All releases',
    prerelease: 'pre-release',
    showRc: 'Show pre-releases',
    build: 'Build details',
    commit: 'commit',
    generated: 'Index generated',
    copyLink: 'Copy link',
    copySha: 'Copy SHA-256',
    copy: 'Copy',
    copied: 'Copied',
  },
  zh: {
    loading: '正在加载版本列表…',
    failed: '无法加载版本索引',
    latest: '最新版本',
    install: '在 Linux x86_64 上安装最新 daemon',
    downloads: '下载',
    releases: '全部版本',
    prerelease: '预发布',
    showRc: '显示预发布版本',
    build: '构建信息',
    commit: 'commit',
    generated: '索引生成于',
    copyLink: '复制链接',
    copySha: '复制 SHA-256',
    copy: '复制',
    copied: '已复制',
  },
};
type Text = typeof TEXT.en;

const PLATFORM_LABEL: Record<string, string> = {
  'linux-x86_64': 'Linux x86_64',
  'linux-aarch64': 'Linux arm64',
  'linux-riscv64': 'Linux riscv64',
  'windows-x86_64': 'Windows x86_64',
};

function fileUrl(template: string, version: string, file: FileEntry): string {
  return template.replace('{version}', `v${version}`).replace('{path}', file.path);
}

function megabytes(bytes: number): string {
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

async function copyText(text: string): Promise<void> {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  // Older browsers and non-secure origins: copy through a hidden textarea.
  const area = document.createElement('textarea');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.position = 'fixed';
  area.style.opacity = '0';
  document.body.appendChild(area);
  area.select();
  document.execCommand('copy');
  area.remove();
}

function CopyButton({ text, label, done }: { text: string; label: string; done: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      className={copied ? 'aiod-copy aiod-copy-done' : 'aiod-copy'}
      title={text}
      onClick={() => {
        copyText(text).then(() => {
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        });
      }}
    >
      {copied ? done : label}
    </button>
  );
}

// Inline markdown: `code`, **bold**, [text](url). Enough for CHANGELOG lines.
function inline(text: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = /`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)/g;
  let last = 0;
  let m: RegExpExecArray | null = re.exec(text);
  while (m) {
    if (m.index > last) out.push(text.slice(last, m.index));
    if (m[1] !== undefined) out.push(<code key={m.index}>{m[1]}</code>);
    else if (m[2] !== undefined) out.push(<strong key={m.index}>{m[2]}</strong>);
    else out.push(<a key={m.index} href={m[4]}>{m[3]}</a>);
    last = m.index + m[0].length;
    m = re.exec(text);
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

// Block markdown for the CHANGELOG subset: "### heading", "- item" with
// two-space nesting, continuation lines, blank-line separated paragraphs.
function Notes({ markdown }: { markdown: string }) {
  type Item = { text: string; children: Item[] };
  const blocks: ReactNode[] = [];
  let list: Item[] = [];
  let para: string[] = [];
  const flushPara = () => {
    if (para.length) blocks.push(<p key={blocks.length}>{inline(para.join(' '))}</p>);
    para = [];
  };
  const renderList = (items: Item[]): ReactNode => (
    <ul>
      {items.map((it, i) => (
        <li key={i}>
          {inline(it.text)}
          {it.children.length > 0 && renderList(it.children)}
        </li>
      ))}
    </ul>
  );
  const flushList = () => {
    if (list.length) blocks.push(<div key={blocks.length}>{renderList(list)}</div>);
    list = [];
  };
  for (const raw of markdown.split('\n')) {
    const heading = /^#{2,4}\s+(.*)$/.exec(raw);
    const bullet = /^(\s*)[-*]\s+(.*)$/.exec(raw);
    if (heading) {
      flushList();
      flushPara();
      blocks.push(<h4 key={blocks.length}>{inline(heading[1])}</h4>);
    } else if (bullet) {
      flushPara();
      const item = { text: bullet[2], children: [] };
      if (bullet[1].length >= 2 && list.length) list[list.length - 1].children.push(item);
      else list.push(item);
    } else if (raw.trim() === '') {
      flushList();
      flushPara();
    } else if (list.length) {
      // continuation of the previous bullet (CHANGELOG wraps long lines)
      const parent = list[list.length - 1];
      const target = parent.children.length ? parent.children[parent.children.length - 1] : parent;
      target.text += ` ${raw.trim()}`;
    } else {
      para.push(raw.trim());
    }
  }
  flushList();
  flushPara();
  return <div className="aiod-notes">{blocks}</div>;
}

// Most common platform first; anything unknown keeps the manifest order after them.
const PLATFORM_ORDER = Object.keys(PLATFORM_LABEL);
function byPlatform(a: Artifact, b: Artifact): number {
  const rank = (p: string) => (PLATFORM_ORDER.includes(p) ? PLATFORM_ORDER.indexOf(p) : PLATFORM_ORDER.length);
  return rank(a.platform) - rank(b.platform);
}

// One tile per platform; every file gets its download link and copy buttons.
function Platforms({ release, template, t }: { release: Manifest; template: string; t: Text }) {
  return (
    <div className="aiod-platforms">
      {[...release.artifacts].sort(byPlatform).map((a) => (
        <div className="aiod-platform" key={a.platform}>
          <div className="aiod-platform-name">
            {PLATFORM_LABEL[a.platform] ?? a.platform}
            {a.libc && <span className="aiod-muted"> · {a.libc}</span>}
          </div>
          {a.files.map((f) => {
            const url = fileUrl(template, release.version, f);
            return (
              <div className="aiod-file" key={f.path}>
                <a className="aiod-file-name" href={url}>
                  {f.path.split('/').pop()}
                </a>
                <span className="aiod-file-size">{megabytes(f.size)}</span>
                <CopyButton text={url} label={t.copyLink} done={t.copied} />
                <CopyButton text={f.sha256} label={t.copySha} done={t.copied} />
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

export function DaemonReleases({
  lang = 'en',
  indexUrl = DEFAULT_INDEX_URL,
  latestUrl = DEFAULT_LATEST_URL,
}: {
  lang?: 'en' | 'zh';
  indexUrl?: string;
  latestUrl?: string;
}) {
  const t = TEXT[lang];
  const [index, setIndex] = useState<Index | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRc, setShowRc] = useState(false);

  useEffect(() => {
    fetch(indexUrl, { cache: 'no-cache' })
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(setIndex)
      .catch((e: Error) => setError(e.message));
  }, [indexUrl]);

  if (error)
    return (
      <p className="aiod-error">
        {t.failed} ({error}): <a href={indexUrl}>{indexUrl}</a>
      </p>
    );
  if (!index) return <p>{t.loading}</p>;

  // File links follow the origin this page is configured for, not the
  // index's mirror list, so a stale template in index.json cannot break them.
  const template = `${new URL(latestUrl).origin}/{version}/{path}`;
  const latest = index.versions.find((v) => v.version === index.latest.stable);
  const visible = index.versions.filter((v) => showRc || v.channel === 'stable');
  const hasRc = index.versions.some((v) => v.channel === 'rc');
  const install = `curl -fsSL ${new URL(latestUrl).origin}/install.sh | sh`;

  return (
    <div className="aiod-releases">
      {latest && (
        <section className="aiod-latest">
          <div className="aiod-latest-title">
            <span className="aiod-latest-label">{t.latest}</span>
            <span className="aiod-latest-version">v{latest.version}</span>
            <span className="aiod-muted">{latest.changelog_date ?? latest.date.slice(0, 10)}</span>
          </div>
          <Platforms release={latest} template={template} t={t} />
          <div className="aiod-install">
            <div className="aiod-install-label">
              {t.install}
              <CopyButton text={install} label={t.copy} done={t.copied} />
            </div>
            <pre>
              <code>{install}</code>
            </pre>
          </div>
        </section>
      )}

      <h2>{t.releases}</h2>
      {hasRc && (
        <label className="aiod-toggle">
          <input type="checkbox" checked={showRc} onChange={(e) => setShowRc(e.target.checked)} /> {t.showRc}
        </label>
      )}
      {visible.map((release) => (
        <section key={release.version} className="aiod-release" id={`v${release.version}`}>
          <h3>
            <a href={`#v${release.version}`}>v{release.version}</a>{' '}
            <small>{release.changelog_date ?? release.date.slice(0, 10)}</small>
            {release.channel === 'rc' && <span className="aiod-badge">{t.prerelease}</span>}
            <small className="aiod-commit">
              {t.commit} <code>{release.source.commit}</code>
            </small>
          </h3>
          <Notes markdown={release.notes} />
          <details>
            <summary>{t.downloads}</summary>
            <Platforms release={release} template={template} t={t} />
          </details>
          <details>
            <summary>{t.build}</summary>
            <ul className="aiod-build">
              {Object.entries(release.build).map(([k, v]) => (
                <li key={k}>
                  <code>{k}</code>: {v ?? '—'}
                </li>
              ))}
            </ul>
          </details>
        </section>
      ))}
      <p className="aiod-generated">
        {t.generated} {index.generated}
      </p>
    </div>
  );
}
