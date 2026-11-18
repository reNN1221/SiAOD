#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback
import math
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список.

    Стабильность: при равенстве ключей элемент из left идёт раньше.
    Ожидаемая сложность: Θ(len(left) + len(right)) - каждый элемент
    берётся ровно один раз.
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. Ожидаемая сложность: Θ(n log n) в любом случае, доп. память O(n). Стабилен."""
    if len(a) <= 1:
        return list(a)
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом: ключи — целые из диапазона [0, key_max].

    Схема: массив счётчиков -> префиксные суммы -> расстановка с конца.
    Ожидаемые время и память: O(n + k), где k = key_max + 1 (размер массива счётчиков)
    ограничение диапазона ключей обсудить в отчёте.
    """
    k = key_max + 1
    count = [0] * k

    # 1. Подсчёт: count[v] = сколько раз встречается v
    for x in a:
        count[x] += 1

    # 2. Префиксные суммы: count[v] = сколько элементов <= v
    for v in range(1, k):
        count[v] += count[v - 1]

    # 3. Расстановка с конца: так равные элементы сохраняют порядок
    result = [0] * len(a)
    for x in reversed(a):
        count[x] -= 1
        result[count[x]] = x
    return result


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам, неотрицательные целые.

    Поверх устойчивой поразрядной counting-сортировки: от младшего разряда
    к старшему. Ожидаемая сложность: Θ(d·(n + b)), где d — число разрядов максимума.
    """
    result = list(a)
    if not result:
        return result
    max_val = max(result)
    exp = 1  # 1 — единицы, 10 — десятки, 100 — сотни
    while max_val // exp > 0:
        # устойчивая сортировка подсчётом по цифре (x // exp) % 10
        count = [0] * 10
        for x in result:
            count[(x // exp) % 10] += 1
        for d in range(1, 10):
            count[d] += count[d - 1]
        out = [0] * len(result)
        for x in reversed(result):  # с конца — устойчивость
            d = (x // exp) % 10
            count[d] -= 1
            out[count[d]] = x
        result = out
        exp *= 10
    return result


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest == i:  # родитель не меньше детей — куча в порядке
            return
        a[i], a[largest] = a[largest], a[i]
        i = largest  # спускаемся туда, куда ушёл элемент


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place: сортирует список a на месте, без вспомогательного массива.

    Схема: построение max-кучи просейками вниз (снизу вверх, O(n)),
    затем обмен вершины с последним элементом и просейка. Сложность: O(n log n) в любом случае, доп. память O(1). Нестабилен.
    """
    n = len(a)
    # 1. Построение кучи: от последнего родителя к корню
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    # 2. Извлечение максимумов
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]  # максимум — в конец
        sift_down(a, 0, end)  # восстанавливаем кучу в a[0:end]


def quick_sort(a: list[int], rng: random.Random | None = None) -> list[int]:
    """QuickSort с рандомизацией опорного элемента (доработка ЛР 3).

    Трёхчастное разбиение (Дейкстра): < p | = p | > p. Равные опорному
    в рекурсию не идут, поэтому много дубликатов не ломает алгоритм.
    Рекурсия — в меньшую часть, цикл — в большую: глубина стека O(log n).
    В среднем O(n log n), в худшем O(n^2). Нестабилен.
    """
    if rng is None:
        rng = random.Random()
    a = list(a)

    def sort(lo: int, hi: int) -> None:
        while lo < hi:
            p = a[rng.randrange(lo, hi + 1)]   # случайный опорный
            lt, i, gt = lo, lo, hi

            while i <= gt:
                if a[i] < p:
                    a[lt], a[i] = a[i], a[lt]
                    lt += 1
                    i += 1
                elif a[i] > p:
                    a[i], a[gt] = a[gt], a[i]
                    gt -= 1
                else:
                    i += 1
            # равные p уже на местах [lt, gt]; меньшую часть — рекурсией
            if lt - lo < hi - gt:
                sort(lo, lt - 1)
                lo = gt + 1
            else:
                sort(gt + 1, hi)
                hi = lt - 1

    sort(0, len(a) - 1)
    return a


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    # TODO: добавить собственные проверки (свойство кучи после построения,
    #       устойчивость поразрядного прохода radix) и описать их в отчёте.
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int, out_dir: Path) -> None:
    """Замеры шести сортировок на пяти распределениях, наклоны и log-log графики."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as err:
        raise SystemExit("Не найден matplotlib. Выполни: pip install matplotlib") from err

    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", lambda a: quick_sort(a, random.Random(seed))),
        ("sorted() (эталон)", sorted),
    ]
    dist_names = ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]
    # records[распределение][алгоритм] = [(n, время), ...]
    records = {d: {name: [] for name, _ in algorithms} for d in dist_names}

    # 1. Замеры
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                t = bench(fn, data)
                records[dist_name][algo_name].append((n, t))
                print(f"    {algo_name:>18}: t = {t:.6f} c")

    # 2. Наклоны: t ≈ c·n^k  =>  k = log(t2/t1) / log(n2/n1)
    print("\nНаклоны log-log (по первой и последней точке):")
    for dist_name, by_algo in records.items():
        print(f"  {dist_name}:")
        for algo_name, pts in by_algo.items():
            if len(pts) < 2:
                continue
            (n1, t1), (n2, t2) = pts[0], pts[-1]
            k = math.log(t2 / t1) / math.log(n2 / n1)
            print(f"    {algo_name:>18}: k = {k:.2f}")

    # 3. Графики: один файл на распределение, все алгоритмы на одном графике
    for dist_name, by_algo in records.items():
        fig, ax = plt.subplots()
        for algo_name, pts in by_algo.items():
            if pts:
                ax.loglog([p[0] for p in pts], [p[1] for p in pts], marker="o", label=algo_name)
        ax.set_title(f"{dist_name}: время от размера входа")
        ax.set_xlabel("n (log)")
        ax.set_ylabel("медиана времени, с (log)")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        path = out_dir / f"lab04_{dist_name}.png"
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f"График сохранён: {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    ap.add_argument("--out", default=None, help="папка для графиков (по умолчанию рядом со скриптом)")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    out_dir = Path(args.out).resolve() if args.out else Path(__file__).resolve().parent
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Вариант {args.variant}; seed={seed}")
    self_check()
    run_benchmarks(seed, out_dir)


if __name__ == "__main__":
    main()