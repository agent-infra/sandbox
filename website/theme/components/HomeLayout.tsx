import { useI18n, usePageData } from '@rspress/core/runtime';
import {
  ArrowIcon,
  BrowserIcon,
  FeatAgentIcon,
  FeatDevfriendlyIcon,
  FeatOutofboxIcon,
  FeatProductionIcon,
  FeatSecureIcon,
  FeatUnifiedIcon,
  FilesIcon,
  GithubIcon,
  JupyterIcon,
  McpIcon,
  TerminalIcon,
  VscodeIcon,
} from './icons';
import './HomeLayout.scss';

interface HeroAction {
  theme: string;
  text: string;
  link: string;
}

interface Feature {
  title: string;
  details: string;
  icon: string;
}

const CAP_TAGS = [
  { key: 'browser', labelEn: 'Browser', labelZh: '浏览器', Icon: BrowserIcon },
  { key: 'terminal', labelEn: 'Terminal', labelZh: '终端', Icon: TerminalIcon },
  { key: 'files', labelEn: 'Files', labelZh: '文件', Icon: FilesIcon },
  { key: 'vscode', labelEn: 'VSCode', labelZh: 'VSCode', Icon: VscodeIcon },
  { key: 'jupyter', labelEn: 'Jupyter', labelZh: 'Jupyter', Icon: JupyterIcon },
  { key: 'mcp', labelEn: 'MCP', labelZh: 'MCP', Icon: McpIcon },
];

const FEATURE_ICONS = [
  FeatUnifiedIcon,
  FeatOutofboxIcon,
  FeatSecureIcon,
  FeatAgentIcon,
  FeatDevfriendlyIcon,
  FeatProductionIcon,
];

function CodeWindow() {
  return (
    <div className="ch-code-window">
      <div className="ch-window-bar">
        <div className="ch-dot ch-dot-r" />
        <div className="ch-dot ch-dot-y" />
        <div className="ch-dot ch-dot-g" />
        <div className="ch-window-title">sandbox.py</div>
      </div>
      <div className="ch-code-body">
        <CodeLine n={1}>
          <span className="ch-kw">from</span> agent_sandbox{' '}
          <span className="ch-kw">import</span> Sandbox
        </CodeLine>
        <CodeLine n={2}>
          <span />
        </CodeLine>
        <CodeLine n={3}>
          <span className="ch-cm"># Initialize client</span>
        </CodeLine>
        <CodeLine n={4}>
          client <span className="ch-op">=</span>{' '}
          <span className="ch-fn">Sandbox</span>(base_url
          <span className="ch-op">=</span>
          <span className="ch-str">f&quot;{'${base_url}'}&quot;</span>)
        </CodeLine>
        <CodeLine n={5}>
          home_dir <span className="ch-op">=</span> client
          <span className="ch-op">.</span>sandbox
          <span className="ch-op">.</span>
          <span className="ch-fn">get_context</span>()
          <span className="ch-op">.</span>home_dir
        </CodeLine>
        <CodeLine n={6}>
          <span />
        </CodeLine>
        <CodeLine n={7}>
          <span className="ch-cm"># Execute shell commands</span>
        </CodeLine>
        <CodeLine n={8}>
          result <span className="ch-op">=</span> client
          <span className="ch-op">.</span>shell<span className="ch-op">.</span>
          <span className="ch-fn">exec_command</span>(
          <span className="ch-str">&quot;ls -la&quot;</span>)
        </CodeLine>
        <CodeLine n={9}>
          <span className="ch-fn">print</span>(result
          <span className="ch-op">.</span>data<span className="ch-op">.</span>
          output)
        </CodeLine>
        <CodeLine n={10}>
          <span />
        </CodeLine>
        <CodeLine n={11}>
          <span className="ch-cm"># File operations</span>
        </CodeLine>
        <CodeLine n={12}>
          content <span className="ch-op">=</span> client
          <span className="ch-op">.</span>file<span className="ch-op">.</span>
          <span className="ch-fn">read_file</span>(
          <span className="ch-str">f&quot;{'${home_dir}'}/.bashrc&quot;</span>)
        </CodeLine>
        <CodeLine n={13}>
          <span className="ch-fn">print</span>(content
          <span className="ch-op">.</span>data<span className="ch-op">.</span>
          content)
        </CodeLine>
        <CodeLine n={14}>
          <span />
        </CodeLine>
        <CodeLine n={15}>
          <span className="ch-cm"># Browser automation</span>
        </CodeLine>
        <CodeLine n={16}>
          screenshot <span className="ch-op">=</span> client
          <span className="ch-op">.</span>browser
          <span className="ch-op">.</span>
          <span className="ch-fn">screenshot</span>()
        </CodeLine>
      </div>
    </div>
  );
}

function CodeLine({ n, children }: { n: number; children: React.ReactNode }) {
  return (
    <div className="ch-code-line">
      <span className="ch-ln">{n}</span>
      <span>{children}</span>
    </div>
  );
}

const SUBTITLE = {
  en: 'One Docker container with browser, terminal, filesystem, VSCode, Jupyter, and MCP Server — accessible via a single API/SDK.',
  zh: '单一 Docker 容器，集成浏览器、终端、文件系统、VSCode、Jupyter 和 MCP 服务器 —— 通过单一 API/SDK 即可访问。',
};

const SECTION_TITLE = {
  en: 'Everything your agent needs,\nout of the box',
  zh: 'AI Agent 所需一切，开箱即用',
};

const SECTION_DESC = {
  en: 'No more juggling multiple services. AIO Sandbox ships a complete, pre-wired environment in a single Docker container.',
  zh: '无需管理多个服务。AIO Sandbox 在单个 Docker 容器中提供完整的预配置环境。',
};

export default function HomeLayout() {
  const { page } = usePageData();
  const t = useI18n();
  const fm = page.frontmatter as Record<string, unknown>;
  const hero = (fm?.hero || {}) as {
    name?: string;
    text?: string;
    tagline?: string;
    actions?: HeroAction[];
  };
  const features = (fm?.features || []) as Feature[];
  const isZh = page.lang === 'zh';

  const titleLines = (hero.text || '').trim().split('\n').filter(Boolean);
  const subtitle = isZh ? SUBTITLE.zh : SUBTITLE.en;
  const footerMessage = t('footerMessage');

  return (
    <div className="ch-home">
      {/* Hero Section */}
      <section className="ch-hero">
        <div className="ch-hero-glow" />
        <div className="ch-hero-inner">
          <div className="ch-hero-content">
            <h1 className="ch-hero-title">
              {titleLines.map((line, i) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                <span key={i}>
                  {line.trim().toLowerCase().includes('ai agent') ? (
                    <span className="ch-gradient-text">{line.trim()}</span>
                  ) : (
                    <span>{line.trim()}</span>
                  )}
                  {i < titleLines.length - 1 && <br />}
                </span>
              ))}
            </h1>
            <p className="ch-hero-subtitle">{subtitle}</p>
            <div className="ch-hero-caps">
              {CAP_TAGS.map(({ key, labelEn, labelZh, Icon }, i) => (
                <span key={key}>
                  <span className="ch-cap-tag">
                    <Icon />
                    {isZh ? labelZh : labelEn}
                  </span>
                  {i < CAP_TAGS.length - 1 && (
                    <span className="ch-cap-sep">/</span>
                  )}
                </span>
              ))}
            </div>
            {hero.actions && (
              <div className="ch-hero-cta">
                {hero.actions.map((action, i) => (
                  <a
                    // biome-ignore lint/suspicious/noArrayIndexKey: <explanation>
                    key={i}
                    href={action.link}
                    className={
                      action.theme === 'brand'
                        ? 'ch-btn-primary'
                        : 'ch-btn-ghost'
                    }
                    {...(action.link.startsWith('http')
                      ? { target: '_blank', rel: 'noopener noreferrer' }
                      : {})}
                  >
                    {action.theme === 'alt' && <GithubIcon />}
                    {action.text}
                    {action.theme === 'brand' && <ArrowIcon />}
                  </a>
                ))}
              </div>
            )}
          </div>

          <div className="ch-hero-visual">
            <div className="ch-floating-badge ch-fb-1">
              <span className="ch-fb-dot" />
              Sandbox running
            </div>
            <CodeWindow />
            <div className="ch-floating-badge ch-fb-2">
              <span className="ch-fb-dot ch-fb-dot-b" />
              MCP Server active
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="ch-features-section">
        <div className="ch-section-inner">
          {/* biome-ignore lint/suspicious/noCommentText: <explanation> */}
          <span className="ch-section-label">// capabilities</span>
          <h2 className="ch-section-title">
            {(isZh ? SECTION_TITLE.zh : SECTION_TITLE.en)
              .split('\n')
              .map((line, i, arr) => (
                // biome-ignore lint/suspicious/noArrayIndexKey: static content
                <span key={i}>
                  {line}
                  {i < arr.length - 1 && <br />}
                </span>
              ))}
          </h2>
          <p className="ch-section-desc">
            {isZh ? SECTION_DESC.zh : SECTION_DESC.en}
          </p>
          <div className="ch-feature-grid">
            {features.map((feature, i) => {
              const IconComp = FEATURE_ICONS[i];
              const isBlue = i % 2 === 1;
              return (
                <div className="ch-feature-card" key={feature.title}>
                  <div className={`ch-feature-icon ${isBlue ? 'blue' : ''}`}>
                    {IconComp ? <IconComp /> : <span>{feature.icon}</span>}
                  </div>
                  <div className="ch-feature-title">{feature.title}</div>
                  <p className="ch-feature-desc">{feature.details}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Footer */}
      {footerMessage && (
        <footer className="ch-footer">
          <div
            className="ch-footer-text"
            // biome-ignore lint/security/noDangerouslySetInnerHtml: <explanation>
            dangerouslySetInnerHTML={{ __html: footerMessage }}
          />
        </footer>
      )}
    </div>
  );
}
