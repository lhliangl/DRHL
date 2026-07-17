from __future__ import annotations

from typing import Callable

from ..config import PipelineConfig
from ..database import Snapshot
from ..errors import CrawlError, DatabaseError
from ..io import read_json, write_json
from ..models import RoleCrawl
from ..progress import progress
from .selenium import SeleniumRoleCrawler


def load_role_artifacts(config: PipelineConfig) -> list[RoleCrawl]:
    crawls = []
    for role in config.roles:
        assert role.artifact is not None
        progress(f"读取角色产物：{role.name} <- {role.artifact}")
        crawl = RoleCrawl.from_dict(read_json(role.artifact))
        if crawl.role != role.name or crawl.kind != role.kind:
            raise CrawlError(f"artifact identity does not match configured role: {role.name}")
        crawls.append(crawl)
    return crawls


def crawl_all_roles(
    config: PipelineConfig,
    snapshot: Snapshot,
    crawler_factory: Callable[[PipelineConfig], SeleniumRoleCrawler] = SeleniumRoleCrawler,
) -> list[RoleCrawl]:
    """Crawl each role in a fresh browser and restore one shared baseline afterward."""
    progress("正在创建数据库基线快照……")
    snapshot_path = snapshot.create()
    progress(f"数据库基线快照完成：{snapshot_path}")
    output_dir = config.run_dir / "crawl"
    results = []
    total = len(config.roles)

    for index, role in enumerate(config.roles, 1):
        progress(f"开始角色 {index}/{total}：{role.name}（{role.kind}）")
        crawler = crawler_factory(config)
        crawl_error: BaseException | None = None
        crawl_result: RoleCrawl | None = None
        try:
            crawl_result = crawler.crawl(role)
            output = output_dir / f"{role.name}.json"
            write_json(output, crawl_result.to_dict())
            progress(
                f"角色 {role.name} 爬取完成：{len(crawl_result.nodes)} 个页面，"
                f"{len(crawl_result.edges)} 条边 -> {output}"
            )
        except BaseException as exc:
            crawl_error = exc
            progress(f"角色 {role.name} 爬取失败：{type(exc).__name__}: {exc}")
        finally:
            try:
                crawler.close()
                progress(f"角色 {role.name} 浏览器已关闭")
            except BaseException as exc:
                if crawl_error is None:
                    crawl_error = exc
            try:
                progress(f"正在恢复角色 {role.name} 爬取前的数据库基线……")
                snapshot.restore()
                progress(f"角色 {role.name} 数据库恢复完成")
            except BaseException as exc:
                raise DatabaseError(
                    f"database restore failed after role {role.name!r}; stopped before the next role: "
                    f"{type(exc).__name__}: {exc}"
                ) from exc
        if crawl_error is not None:
            raise CrawlError(f"crawl failed for role {role.name!r}") from crawl_error
        assert crawl_result is not None
        results.append(crawl_result)
    return results

