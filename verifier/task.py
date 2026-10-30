"""extract-companies: the submitted companies against the answer key pinned from the snapshot by code."""

from .checks import constraint, result, verdict

FIRST_YEAR, LAST_YEAR = 2005, 2026
FIELDS = ("name", "season", "year", "industry", "sub_industry", "city", "country")


def filter_problem(task):
    if not FIRST_YEAR <= task.year_from <= task.year_to <= LAST_YEAR:
        return f"years must satisfy {FIRST_YEAR} <= year_from <= year_to <= {LAST_YEAR}"
    if task.industry != task.industry.strip():
        return "industry must not start or end with spaces"
    return None


def keeps(task, record):
    return (
        (not task.industry or record.industry.casefold() == task.industry.casefold())
        and (task.season.value == "any" or record.season.value == task.season.value)
        and task.year_from <= record.year <= task.year_to
    )


def plain(record):
    return {
        "slug": record.slug,
        "name": record.name,
        "season": record.season.value,
        "year": record.year,
        "industry": record.industry,
        "sub_industry": record.sub_industry,
        "city": record.city,
        "country": record.country,
    }


# pin_matches is the reference tool: its own input and output are checked like any tool call.
def verify_input(value):
    problem = filter_problem(value)
    return result(False, problem) if problem else result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    if output_value.count != len(output_value.companies):
        return result(False, "count is not the number of companies")
    wrong = [record.slug for record in output_value.companies if not keeps(input_value, record)]
    if wrong:
        return result(False, f"companies outside the filter: {wrong}")
    return result(True, f"{output_value.count} companies match")


def verify_task(arguments, output, reference, workspace):
    problem = filter_problem(arguments)
    if problem:
        return result(False, problem)
    if reference is None:
        return result(False, "no answer key was pinned")
    expected = {record.slug: plain(record) for record in reference.companies}
    order = [record.slug for record in reference.companies]
    submitted = [record.slug for record in output.companies]
    got = {record.slug: plain(record) for record in output.companies}

    duplicates = sorted({slug for slug in submitted if submitted.count(slug) > 1})
    missing = [slug for slug in order if slug not in got]
    extra = [slug for slug in submitted if slug not in expected]
    outside = [record.slug for record in output.companies if not keeps(arguments, record)]
    wrong = []
    for slug in order:
        if slug in got:
            for field in FIELDS:
                if got[slug][field] != expected[slug][field]:
                    wrong.append(f"{slug}.{field}: expected {expected[slug][field]!r}, got {got[slug][field]!r}")
    in_order = [slug for slug in submitted if slug in expected] == [slug for slug in order if slug in got]

    return verdict([
        constraint("count", "count equals the number of companies submitted", output.count == len(submitted),
                   len(submitted), output.count),
        constraint("no-duplicates", "each company appears once", not duplicates, [], duplicates,
                   f"submitted more than once: {duplicates}"),
        constraint("within-filter", "every submitted record satisfies the filter by its own fields", not outside,
                   [], outside, f"records that do not satisfy the filter: {outside}"),
        constraint("no-missing", "every matching company is submitted", not missing, [], missing,
                   f"{len(missing)} matching companies are missing: {missing}"),
        constraint("no-extra", "no company outside the answer key is submitted", not extra, [], extra,
                   f"{len(extra)} companies do not match: {extra}"),
        constraint("fields-exact", "every field equals the card's", not wrong, [], wrong,
                   f"{len(wrong)} fields differ, first: {wrong[0] if wrong else ''}"),
        constraint("directory-order", "companies are in directory order", in_order, order, submitted,
                   "companies are not in directory order"),
    ])
